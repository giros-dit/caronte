from flask import Blueprint, render_template, request, flash, redirect, url_for, session, make_response
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_oidc.signals import after_authorize
from functools import wraps
from datetime import timedelta
import os
import requests
import json

from app import oidc, config
from database import db_session
from models import User, Ownership, Machine
import mail.mail as mail
from utils import logger

auth = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None:
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.admin is False:
            if request.headers.get('HX-Request') == 'true':
                response = make_response(redirect(url_for('views.index')), 403)
                response.headers['HX-Trigger-After-Settle'] = '''{"new-toast": {"type": "error", "message": "No tienes permiso para acceder a este recurso.", "title": "Forbidden", "options": {}}}'''
            else:   
                response = make_response('Forbidden', 403)

            logger.debug(f"User {current_user.username} attempted to access an admin-only resource.")
            return response
        return f(*args, **kwargs)
    return decorated_function

def authorization_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):      
        machine_id = kwargs.get('machineId')
        ownership = Ownership.query.filter_by(user_id=current_user.id, machine_id=machine_id).first()
        
        if not current_user.admin and not hasattr(current_user, 'service') and ownership is None:
            if request.headers.get('HX-Request') == 'true':
                response = make_response(redirect(url_for('views.index')), 403)
                response.headers['HX-Trigger-After-Settle'] = '''{"new-toast": {"type": "error", "message": "No tienes permiso para acceder a este recurso.", "title": "Forbidden", "options": {}}}'''
            else:   
                response = make_response('Forbidden', 403)
                
            logger.debug(f"User {current_user.username} attempted to access an authorized resource.")
            return response
        return f(*args, **kwargs)
    return decorated_function

def generate_recovery_token(user):
    try:
        recoveryToken = os.urandom(32).hex()
        user.setRecoveryToken(recoveryToken)
        db_session.commit() 
        
    except:
        response = make_response('', 500)
        toast = {"type": "error",
                 "message": "Se ha producido un error al generar el token de recuperación.",
                 "title": "Error al generar token",
                 "options": {}
                }
        response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
        
        logger.error(f"Error generating recovery token for user {user.username}.")
        raise RuntimeError(response)
                   
    try:
        mail.sendMail(
            user.email,
            f"Reestablecimiento de contraseña en {config['SERVER_NAME']}",
            mail.buildMessage('resetPassword', {'$RECOVERY_URL': f"{config['SERVER_URL']}/reset-password?token={recoveryToken}"})
        )

        logger.info(f"Recovery email sent to user {user.username}.")
        return
        
    except Exception as e:
        response = make_response('', 500)
        toast = {"type": "error",
                    "message": "Se ha producido un error al enviar el correo de restablecimiento.",
                    "title": "Error al enviar mensaje",
                    "options": {}
                }
        response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
        
        logger.error(f"Error sending recovery email to user {user.username}: {e}")
        raise RuntimeError(response)
    

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        user = User.query.filter(
            (User.username == user_id) |
            (User.email == user_id)
        ).first()
        
        toast = {"type": "error",
            "message": "Nombre de usuario o contraseña incorrectos.",
            "title": "Inicio de sesión fallido",
            "options": {}
            }
        
        response = make_response('', 401)
        response.headers['HX-Trigger'] = f'{{"new-toast": {json.dumps(toast)} }}'
        
        if user:
            if check_password_hash(user.password, password):
                login_user(user, duration=timedelta(minutes=30))
                
                response = make_response('', 200)
                response.headers['HX-Redirect'] = '/'
            
        return response
                        
    elif request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('views.index'))
        else:
            return render_template("login.html")     

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        
        user = User.query.filter(
            (User.username == user_id) |
            (User.email == user_id)
        ).first()   
             
        if user:
            try:
                generate_recovery_token(user)         
                toast = {"type": "success",
                        "message": "Se ha enviado un correo electrónico para restablecer la contraseña. Vuelve a la página de inicio de sesión para continuar.",
                        "title": "Mensaje enviado",
                        "options": {}   
                }
                
                response = make_response('', 200)
                response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
                
            except RuntimeError as e:
                response = e
                
        else:
            toast = {"type": "error",
                    "message": "El usuario o email especificado no está registrado.",
                    "title": "Usuario no encontrado",
                    "options": {}   
            }
            response = make_response('', 404)
            response.headers['HX-Trigger'] = f'{{"new-toast": {json.dumps(toast)} }}'
          
        return response
        
    elif request.method == 'GET':
        return render_template("forgot_password.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    
    if hasattr(oidc, 'logout'):
        oidc.logout() 
    session.clear()
    
    return redirect(url_for('auth.login'))      

def handle_oidc_login(sender, **kwargs):
    if oidc.user_loggedin:
        user_info = session.get("oidc_auth_profile", {})
        
        username = user_info.get('sub')
        email = user_info.get('email')
        admin = any(group in user_info.get('groups', []) for group in config['OIDC_ADMIN_GROUPS'].split(' '))

        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(username=username, email=email, external=True, admin=admin)
        
        else:
            user.username = username
            user.email = email
            user.external = True
            # User will be admin if they belong to any of the groups specified in OIDC_ADMIN_GROUPS
            user.admin = admin

        try:
            db_session.add(user)
            db_session.commit()
        except Exception as e:
            flash('Error creating/updating user data.', category='error')
            return redirect(url_for('auth.login'))
            
        login_user(user)

def _load_oidc_client_secrets():
    client_secrets_file = config.get('OIDC_CLIENT_SECRETS', 'client_secrets.json')
    with open(client_secrets_file, 'r') as file_handle:
        data = json.load(file_handle)

    return data.get('web', {})

def _get_jwt_token(client_secret):
    oidc_config = _load_oidc_client_secrets()
    token_endpoint = oidc_config.get('token_uri')
    client_id = oidc_config.get('client_id')

    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'openid profile groups'
    }

    response = requests.post(token_endpoint, data=payload)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None
    
def _get_user_info(jwt_token):
    oidc_config = _load_oidc_client_secrets()
    userinfo_endpoint = oidc_config.get('userinfo_uri')

    headers = {
        'Authorization': f'Bearer {jwt_token}'
    }

    response = requests.get(userinfo_endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def authentication_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        client_secret = request.args.get('client_secret')
        jwt_token = request.args.get('jwt_token')

        if not jwt_token and client_secret:
            jwt_token = _get_jwt_token(client_secret)
            
        if jwt_token:
            user_info = _get_user_info(jwt_token)
            if user_info:
                current_user = User(username=user_info.get('sub'), external=True)
                current_user.service = any(group in user_info.get('groups', []) for group in config['OIDC_SERVICE_GROUPS'].split(' '))

                login_user(current_user)                    
                return f(*args, **kwargs)
            else:
                return 'Forbidden', 403
        else:
            return login_required(f)(*args, **kwargs)

    return wrapper

after_authorize.connect(handle_oidc_login)