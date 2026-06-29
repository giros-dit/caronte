from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_oidc.signals import after_authorize
from functools import wraps
from datetime import timedelta

from app import oidc, config
from database import db_session
from models import User

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

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        remember = True if request.form.get('remember') != None else False

        user = User.query.filter(
            (User.username == user_id) |
            (User.email == user_id)
        ).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=remember, duration=timedelta(minutes=30))
                return redirect(url_for('views.index'))
            else:
                flash('Contraseña incorrecta.', category='error')
        else:
            flash('El usuario o email especificado no está registrado.', category='error')
    elif request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('views.index'))
        else:
            return render_template("login.html", TITLE=config.TITLE)     

@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Limpia Flask-Login
    
    # NUEVO: Limpia el estado de Flask-OIDC y destruye los tokens del servidor
    if hasattr(oidc, 'logout'):
        oidc.logout() 
    session.clear()  # Borra por completo el contenido de Flask-Session
    
    return redirect(url_for('auth.login'))      

def handle_oidc_login(sender, **kwargs):
    if oidc.user_loggedin:
        user_info = session.get("oidc_auth_profile", {})
        
        username = user_info.get('sub')
        email = user_info.get('email')

        if not email:
            flash('El proveedor OIDC no ha devuelto un email válido.', category='error')
            return

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email, external=True)
            db_session.add(user)
            db_session.commit()
            
        login_user(user)

after_authorize.connect(handle_oidc_login)