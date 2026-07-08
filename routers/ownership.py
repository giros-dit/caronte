from flask import Blueprint, request, render_template, flash
from flask_login import login_required

from models import User, Machine, Ownership
from database import db_session
from auth import admin_required

ownership = Blueprint('ownership', __name__)

@ownership.route('/admin/ownership/<int:userId>/machines/<int:machineId>', methods=['GET',  'PUT', 'DELETE'])
@login_required
@admin_required
def assign_machine(userId, machineId):
    user = User.query.get(userId)
    machine = Machine.query.get(machineId)
       
    if user:
        if machine:
            if request.method == 'GET':
                ownership = Ownership.query.filter_by(user_id=userId, machine_id=machineId).first()
                machine.is_owned = ownership is not None
                return render_template('ownership/row.html', user=user, machine=machine)
            if request.method == 'PUT':
                ownership = Ownership.query.filter_by(user_id=userId, machine_id=machineId).first()
                if not ownership:
                    ownership = Ownership(user_id=userId, machine_id=machineId)
                    db_session.add(ownership)
                db_session.commit()
                machine.is_owned = True
                return render_template('ownership/row.html', user=user, machine=machine)
            elif request.method == 'DELETE':
                ownership = Ownership.query.filter_by(user_id=userId, machine_id=machineId).first()
                if ownership:
                    db_session.delete(ownership)
                db_session.commit()
                machine.is_owned = False
                return render_template('ownership/row.html', user=user, machine=machine)
        else:
            return flash('Machine not found.', category='error'), 404
    else:
        return flash('User not found.', category='error'), 404
