from flask import request, redirect, url_for
from flask_login import login_required, LoginManager

import os

from database import init_db, db_session
from models import User
from auth import auth
from views import views
from routers.users import users as usersRouter
from routers.machines import machines as machinesRouter
from routers.ownership import ownership as ownershipRouter
from routers.api import api as apiRouter

from app import config

login_manager = LoginManager()

from app import app

init_db()

users = User.query.all()
if users == []:
    print("No users found, creating default admin user with random password...")
    adminPassword = os.urandom(8).hex()
    newUser = User(username="admin", email=None, password=adminPassword)
    newUser.admin = True
    newUser.activated = True
    try:
        db_session.add(newUser)
        db_session.commit()
    except Exception as e:
        print("Error creating default admin user: " + str(e))
    finally:
        print(f"Default 'admin' user created with password: {adminPassword} \n\n")


app.secret_key = config['SECRET']
app.register_blueprint(auth) 
app.register_blueprint(views)
app.register_blueprint(usersRouter)
app.register_blueprint(machinesRouter)
app.register_blueprint(ownershipRouter)
app.register_blueprint(apiRouter)
login_manager.login_view = "auth.login"
login_manager.login_message = None
login_manager.init_app(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))