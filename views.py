from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user

from auth import admin_required
from models import User, Machine, Ownership
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


@views.route('/admin/machines', methods=['GET'])
@login_required
def machines():
    if current_user.admin:
        if request.method == 'GET':
            machines = Machine.query.all()
            return render_template('machines/main.html', machines=machines)  
    else:
        abort(403)


@views.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('users/main.html', users=users)

@views.route('/admin/ownership/<int:userId>/machines', methods=['GET'])
@login_required
def user_machines(userId):
    if current_user.admin:
        if request.method == 'GET':
            user = User.query.get(userId)
            if user:
                machines = Machine.query.all()
                
                # Consulta limpia de IDs
                ownerships = [o[0] for o in Ownership.query.filter_by(user_id=userId).with_entities(Ownership.machine_id).all()]

                # Marcado con un atributo temporal nuevo
                for machine in machines:
                    machine.is_owned = machine.id in ownerships
                
                return render_template('ownership/main.html', user=user, machines=machines)
            else:
                return abort(404)
    else:
        abort(403)