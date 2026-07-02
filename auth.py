from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_oidc.signals import after_authorize
from functools import wraps
from datetime import timedelta
import os

from app import oidc, config
from database import db_session
from models import User
import mail.mail as mail

auth = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None:
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.admin is False:
            flash('You have no permission to access this resource.', category='error')
            return redirect(url_for('views.index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_recovery_token(user):
    try:
        recoveryToken = os.urandom(32).hex()
        user.setRecoveryToken(recoveryToken)
        db_session.commit()                
        try:
            mail.sendMail(
                user.email,
                f"Reestablecimiento de contraseña en {config['SERVER_NAME']}",
                mail.buildMessage('resetPassword', {'$RECOVERY_URL': f"{config['SERVER_URL']}/reset-password?token={recoveryToken}"})
            )

            return True
        except Exception as e:
            raise Exception("Error sending reset email.")
    except:
        raise Exception("Error generating recovery token.")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        user = User.query.filter(
            (User.username == user_id) |
            (User.email == user_id)
        ).first()
        
        if user:
            if check_password_hash(user.password, password):
                login_user(user, duration=timedelta(minutes=30))
                return redirect(url_for('views.index'))
            else:
                flash('Contraseña incorrecta.', category='error')
                return render_template("login.html"), 401
        else:
            flash('El usuario o email especificado no está registrado.', category='error')
            return render_template("login.html"), 404
                        
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
            if generate_recovery_token(user):
                flash('Se ha enviado un correo electrónico para restablecer la contraseña.', category='success')
                return redirect(url_for('auth.login'))
        else:
            flash('El email especificado no está registrado.', category='error')
            return render_template("forgot_password.html"), 404
        
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

after_authorize.connect(handle_oidc_login)