from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user

from models import User, Machine, Ownership
from app import config
views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def index():
    if request.method == 'GET':
        machines = []
        if hasattr(current_user, 'admin'):
            owner = Ownership.query.filter_by(user_id = current_user.id).all()
            for machine in owner:
                machines.append(Machine.query.get(machine.machine_id))
        return render_template('index.html', machines=machines)


@views.route('/machines', methods=['GET'])
@login_required
def machines():
    if current_user.admin:
        if request.method == 'GET':
            machines = Machine.query.all()
            return render_template('machines.html', machines=machines)  
    else:
        abort(403)


@views.route('/users', methods=['GET'])
@login_required
def users():
    if current_user.admin:
        
        # Recupera los datos de todos los usuarios.
        if request.method == "GET":

            users = User.query.all()
            return render_template('users/main.html', users=users, currentUserId=current_user.id)

    else:
        abort(403)


@views.route('/users/<int:user_id>/machines', methods=['GET'])
@login_required
def user_machines(user_id):
    if current_user.admin:
        if request.method == 'GET':
            machines = Machine.query.all()
            ownerships = Ownership.query.filter_by(user_id=user_id).all()
            user = User.query.get(user_id).username
            owned_machines = []
            for machine in ownerships:
                owned_machines.append(machine.machine_id)
            return render_template('ownership.html', user=user, machines=machines, owned_machines=owned_machines)
    else:
        abort(403)