from flask import Blueprint, request, abort, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
from auth import admin_required
import random
import string
import re
import os

from models import User, Machine, Ownership
from database import db_session
import mail.mail as mail
from app import config

users = Blueprint('users', __name__)

@users.route('/users/<int:userId>', methods=['GET'])
@login_required
@admin_required
def get_user(userId):
    user = User.query.get(userId)
    if user:
        return render_template('users/row.html', user=user, TITLE=config['TITLE'], isAdmin=current_user.admin)
    else:
        return flash('User not found.', category='error'), 404
        
@users.route('/users/<int:userId>/edit', methods=['GET'])
@login_required
@admin_required
def edit_user(userId):
    user = User.query.get(userId)
       
    if user:
        return render_template('users/editableRow.html', user=user, TITLE=config['TITLE'], isAdmin=current_user.admin)
    else:
        return flash('User not found.', category='error'), 404

@users.route('/users/new', methods=['GET'])
@login_required
@admin_required
def new_user():
    return render_template('users/newRow.html', TITLE=config['TITLE'], isAdmin=current_user.admin), 200

@users.route('/users/<int:userId>', methods=['PATCH', 'PUT', 'DELETE'])
@login_required
@admin_required
def update_user(userId):
    
    # Reset user password.
    if request.method == 'PATCH':
        user = User.query.filter_by(id=userId).first()

        if user:
            if user.external:
                return flash('Cannot reset password for external users.', category='error'), 405
            
            try:
                recoveryToken = os.urandom(64).hex()
                User.setRecoveryToken(user, recoveryToken)
                db_session.commit()                

                try:
                    mail.sendMail(
                        user.email,
                        f"Reestablecimiento de contraseña en {config['SERVER_NAME']}",
                        mail.buildMessage('resetPassword', {'$RECOVERY_URL': f"{config['SERVER_URL']}/reset-password?token={recoveryToken}"})
                    )
                    
                    flash('Password reset email sent successfully.', category='success')
                    return '', 200
                except Exception as e:
                    print(e)
                    return flash('Error sending reset email.', category='error'), 500
            except:
                return flash('Error generating recovery token.', category='error'), 500
        else:
            return flash('User not found.', category='error'), 404
    
    # Update user data.
    elif request.method == 'PUT':
        user = User.query.filter_by(id=userId).first()
        if user:
            if not user.external:
                updatedUsername = request.form.get('username')
                updatedEmail = request.form.get('email')
                
                if updatedUsername == None:
                    return flash('Username is required.', category='error'), 400
                    
                if updatedEmail == None:
                    return flash('Email is required.', category='error'), 400
                
                regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

                if not (re.fullmatch(regex, updatedEmail)):
                    return flash('Email address is not valid.', category='error'), 400
            
            updatedAdmin = True if request.form.get('admin') else False
                        
            try:
                if not user.external:
                    user.username = updatedUsername
                    user.email = updatedEmail
                user.admin = updatedAdmin or False
                db_session.commit()
                return render_template('users/row.html', user=user, TITLE=config['TITLE'], isAdmin=current_user.admin)
            except:
                return flash('Error updating user data.', category='error'), 500
        else:
            return flash('User not found.', category='error'), 404
    
    # Remove user.
    elif request.method == 'DELETE':
        user = User.query.filter_by(id=userId).first()
        if user:
            try:
                db_session.delete(user)
                db_session.commit()
                flash('User deleted successfully.', category='success')
                return ('', 200)
            except:
                return flash('Cannot delete user.', category='error'), 500
        else:
            return flash('User not found.', category='error'), 404

@users.route('/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    newUsername = request.form.get('username')
    newEmail = request.form.get('email')
    newAdmin = True if request.form.get('admin') else False
    
    if newUsername == None:
        return flash('Username is required.', category='error'), 400
        
    if newEmail == None:
        return flash('Email is required.', category='error'), 400
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, newEmail)):
        return flash('Email address is not valid.', category='error'), 400
    user = User(username=newUsername, email=newEmail, admin=newAdmin or False)
    if user:
        try:
            db_session.add(user)
            db_session.commit()
            flash('User created successfully.', category='success')
            return render_template('users/row.html', user=user, TITLE=config['TITLE'], isAdmin=current_user.admin), 200
        except:
            return flash('Error creating user.', category='error'), 500
    else:
        return flash('User not found.', category='error'), 404

@users.route('/users/<int:userId>/machines', methods=['PUT', 'DELETE'])
@login_required
def user_machines(userId):
    if current_user.admin:

        if request.method == 'PUT':
            try:
                new_ownership = Ownership(user_id=userId, machine_id=request.json["machine_id"])
                db_session.add(new_ownership)
                db_session.commit()
                response = {
                    'code': 0,
                    'isOwned': 1
                }
            except:
                response = {
                    'code': 1,
                    'message': "Error añadiendo propiedad a la máquina {request.json['machine_id']}."
                }
            return response

        elif request.method == 'DELETE':
            try:
                ownership = Ownership.query.filter_by(user_id = userId, machine_id=request.json["machine_id"]).first()
                if ownership:
                    db_session.delete(ownership)
                db_session.commit()
                response = {
                    'code': 0,
                    'isOwned': 0
                }
            except:
                response = {
                    'code': 1,
                    'message': f"Error eliminando la propiedad de la máquina {request.json['machine_id']}."
                }
            return response

    else:
        abort(403)