from flask import Blueprint, request, redirect, url_for, render_template, make_response
from flask_login import login_required

import re, json

from models import User
from database import db_session
from auth import admin_required, generate_recovery_token
import mail.mail as mail
from app import config
from utils import *

users = Blueprint('users', __name__)

@users.route('/admin/users/<int:userId>', methods=['GET'])
@login_required
@admin_required
def get_user(userId):
    try:
        user = getUser(userId)
        response = make_response(render_template('users/row.html', user=user), 200)
    except LookupError as e:
        response = e.args[0]
    
    return response

@users.route('/admin/users/<int:userId>/edit', methods=['GET'])
@login_required
@admin_required
def edit_user(userId):
    try:
        user = getUser(userId)
        response = make_response(render_template('users/editable_row.html', user=user), 200)
    except LookupError as e:
        response = e.args[0]
    
    return response

@users.route('/admin/users/new', methods=['GET'])
@login_required
@admin_required
def new_user():
    return render_template('users/new_row.html'), 200

@users.route('/admin/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    newUsername = request.form.get('username')
    newEmail = request.form.get('email')
    newAdmin = True if request.form.get('admin') else False
    
    toasts = []
    
    if newUsername == None or newUsername.strip() == "":
        response = make_response('', 400)
        
        toast = {"type": "warning",
                 "message": "El nombre de usuario es obligatorio.",
                 "title": "Error al crear usuario",
                 "options": {}
                }

        toasts.append(toast)

    if newEmail == None or newEmail.strip() == "":
        response = make_response('', 400)
        
        toast = {"type": "warning",
                 "message": "El email es obligatorio.",
                 "title": "Error al crear usuario",
                 "options": {}
                }
        
        toasts.append(toast)

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, newEmail)):
        
        toast = {"type": "warning",
                 "message": "La dirección de email no es válida.",
                 "title": "Error al crear usuario",
                 "options": {}
                }
        
        toasts.append(toast)
        
    if len(toasts) > 0:
        response = make_response('', 400)
        response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toasts)} }}'

    else:
        user = User(username=newUsername, email=newEmail, admin=newAdmin or False)
        
        try:
            db_session.add(user)
            db_session.commit()
            toast = {"type": "success",
                     "message": f"Usuario {user.username} creado exitosamente.",
                     "title": "Usuario creado",
                     "options": {}
                    }
            
            response = make_response(render_template('users/row.html', user=user), 200)
        except:
            toast = {"type": "error",
                     "message": f"Error al crear usuario {user.username}.",
                     "title": "Error al crear usuario",
                     "options": {}
                    }
            
            response = make_response('', 500)
            
        response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
    
    return response

@users.route('/admin/users/search', methods=['GET'])
@login_required
@admin_required
def search_users():
    search_query = request.args.get('search', '')
    users = User.query.filter(
        (User.username.ilike(f'%{search_query}%')) | 
        (User.email.ilike(f'%{search_query}%'))
    ).all()
    
    print(users)
    
    return render_template('users/table_contents.html', users=users)

@users.route('/admin/users/<int:userId>', methods=['PATCH', 'PUT', 'DELETE'])
@login_required
@admin_required
def update_user(userId):
    # Request password reset for user.
    if request.method == 'PATCH':
        try:
            user = getUser(userId)
            
            if user.external:
                toast = {"type": "warning",
                         "message": "No se puede restablecer la contraseña de usuarios externos.",
                         "title": "Acción no permitida",
                         "options": {}
                        }
                
                logger.warning(f"Attempted to reset password for external user {user.username}.")
                response = make_response('', 405)

            try:
                generate_recovery_token(user)
                toast = {"type": "success",
                         "message": f"Email de restablecimiento de contraseña enviado exitosamente a {user.email}.",
                         "title": "Mensaje enviado",
                         "options": {}
                        }
            
                response = make_response('', 200)
                
                response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
            
            except RuntimeError as e:
                response = e.args[0]
                
        except LookupError as e:
            response = e.args[0]       
        
        return response
    
    # Update user data.
    elif request.method == 'PUT':
        try:
            user = getUser(userId)

            if not user.external:
                updatedUsername = request.form.get('username')
                updatedEmail = request.form.get('email')
            
                toasts = []
                
                if updatedUsername == None or updatedUsername.strip() == "":
                    response = make_response('', 400)
        
                    toast = {"type": "warning",
                            "message": "El nombre de usuario es obligatorio.",
                            "title": "Error al editar usuario",
                            "options": {}
                            }

                    toasts.append(toast)
                    
                if updatedEmail == None or updatedEmail.strip() == "":
                    response = make_response('', 400)
        
                    toast = {"type": "warning",
                            "message": "El correo electrónico es obligatorio.",
                            "title": "Error al editar usuario",
                            "options": {}
                            }

                    toasts.append(toast)

                regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

                if not (re.fullmatch(regex, updatedEmail)):
                    response = make_response('', 400)
                    
                    toast = {"type": "warning",
                            "message": "La dirección de correo electrónico no es válida.",
                            "title": "Error al editar usuario",
                            "options": {}
                            }
                    
                if len(toasts) > 0:
                    response = make_response('', 400)
                    response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toasts)} }}'
                    
                else:
                    updatedAdmin = True if request.form.get('admin') else False
                                
                    try:
                        if not user.external:
                            user.username = updatedUsername
                            user.email = updatedEmail
                        user.admin = updatedAdmin or False
                        db_session.commit()
                        
                        response = make_response(render_template('users/row.html', user=user), 200)
                        toast = {"type": "success",
                                 "message": f"Usuario {user.username} actualizado correctamente.",
                                 "title": "Usuario actualizado",
                                 "options": {}
                                }
                    except:
                        response = make_response('', 500)
                        toast = {"type": "error",
                                 "message": f"Error al actualizar usuario {user.username}.",
                                 "title": "Error al actualizar usuario",
                                 "options": {}
                                }
                    
                    response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
         
        except LookupError as e:
            response = e.args[0]
                               
        return response
    
    # Remove user.
    elif request.method == 'DELETE':
        try:
            user = getUser(userId)

            try:
                db_session.delete(user)
                db_session.commit()
                
                response = make_response('', 200)
                toast = {"type": "success",
                         "message": f"Usuario {user.username} eliminado exitosamente.",
                         "title": "Usuario eliminado",
                         "options": {}
                        }

            except:
                response = make_response('', 500)
                toast = {"type": "error",
                         "message": f"Error al eliminar usuario {user.username}.",
                         "title": "Error al eliminar usuario",
                         "options": {}
                        }
        
            response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
            
        except LookupError as e:
            response = e.args[0]
            
        return response

@users.route('/reset-password', methods=['GET', 'POST'])
def reset_password():        
    if request.method == 'GET':
        token = request.args.get('token')
        
        if request.headers.get('HX-Request') == 'true':

            try:
                user = getUserByToken(token)
                return render_template('password_reset/form.html', token=token), 200
                
            except LookupError as e:
                response = e.args[0]
                return response

        else:
            return render_template('password_reset/main.html', token=token), 200
    
    elif request.method == 'POST':
        token = request.form.get('token')
        
        try:
            user = getUserByToken(token)

            password = request.form.get('password')
            confirmPassword = request.form.get('confirmPassword')
            
            error_flag = False

            if not password or password == '' or not confirmPassword or confirmPassword == '':
                response = make_response('', 400)
                toast = {"type": "warning",
                         "message": "Por favor, complete todos los campos.",
                         "title": "Error al restablecer contraseña",
                         "options": {}
                        }
                error_flag = True

            if password != confirmPassword:
                response = make_response('', 400)
                toast = {"type": "warning",
                         "message": "Las contraseñas no coinciden.",
                         "title": "Error al restablecer contraseña",
                         "options": {}
                        }
                error_flag = True

            if error_flag:
                response.headers['HX-Trigger'] = f'{{"new-toast": {json.dumps(toast)} }}'
                return response

            try:
                user.setPassword(password)
                user.setRecoveryToken(None)  # Clear the recovery token after successful password reset

                db_session.commit()

                try:
                    mail.sendMail(
                        user.email,
                        f"Contraseña actualizada en {config['SERVER_NAME']}",
                        mail.buildMessage('updatedPassword')
                    )
                    
                except Exception as e:
                    logger.error(f"Error sending password update email: {e}")

                response = make_response('', 200)
                response.headers['HX-Redirect'] = url_for('auth.login')
                
            except:
                response = make_response('', 400)
                toast = {"type": "error",
                         "message": "Ha ocurrido un error al actualizar la contraseña. Por favor, inténtelo de nuevo. Si el problema persiste, contacte con el administrador del sistema.",
                         "title": "Error al actualizar contraseña",
                         "options": {}
                        }
                    
        except LookupError as e:
            response = e.args[0]
            
            
    return response