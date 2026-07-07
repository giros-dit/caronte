from flask import Blueprint, request, render_template, flash, session
from flask_login import login_required
import re

from models import Machine
from database import db_session
from auth import admin_required

machines = Blueprint('machines', __name__)

@machines.route('/machines/<int:machineId>', methods=['GET'])
@login_required
@admin_required
def get_machine(machineId):
    machine = Machine.query.get(machineId)
    if machine:
        return render_template('machines/row.html', machine=machine)
    else:
        return flash('Machine not found.', category='error'), 404

@machines.route('/machines/<int:machineId>/edit', methods=['GET'])
@login_required
@admin_required
def edit_machine(machineId):
    machine = Machine.query.get(machineId)
       
    if machine:
        return render_template('machines/editable_row.html', machine=machine)
    else:
        return flash('Machine not found.', category='error'), 404

@machines.route('/machines/new', methods=['GET'])
@login_required
@admin_required
def new_machine():
    return render_template('machines/new_row.html'), 200

@machines.route('/machines', methods=['POST'])
@login_required
@admin_required
def create_machine():
    newName = request.form.get('name').strip()
    newMac = request.form.get('mac').strip()
    newIp = request.form.get('ip').strip()
    newPort = request.form.get('port').strip()
    
    if newName == None:
        flash('Name is required.', category='error')
        return '', 400
        
    if newMac == None:
        flash('MAC address is required.', category='error')
        return '', 400
    
    if newIp == None:
        flash('IP address is required.', category='error')
        return '', 400

    if newPort == None:
        flash('Port is required.', category='error')
        return '', 400
    
    ipRegex = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    macRegex = r'(?:[0-9a-fA-F]){12}'
    macFullRegex = r'(?:[0-9a-fA-F]:?){12}'
    portRegex = r'^(0|[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$'
    
    if not (re.fullmatch(macRegex, newMac)) and not (re.fullmatch(macFullRegex, newMac)):
        flash('MAC address is not valid.', category='error')
        return '', 400
    
    if (re.fullmatch(macRegex, newMac)):
                newMac = list(newMac)
                newMac.insert(10 ,':')
                newMac.insert(8 ,':')
                newMac.insert(6 ,':')
                newMac.insert(4 ,':')
                newMac.insert(2 ,':')
                newMac = ''.join(newMac)
    
    if not (re.fullmatch(ipRegex, newIp)):
        flash('IP address is not valid.', category='error')
        return '', 400

    if not (re.fullmatch(portRegex, newPort)):
        flash('Port is not valid.', category='error')
        return '', 400
    
    
    machine = Machine(name=newName, mac=newMac, ip=newIp, port=newPort)
    if machine:
        try:
            db_session.add(machine)
            db_session.commit()
            flash('Machine created successfully.', category='success')
            return render_template('machines/row.html', machine=machine), 200
        except:
            return flash('Error creating machine.', category='error'), 500
    else:
        return flash('Machine not found.', category='error'), 404

@machines.route('/machines/search', methods=['GET'])
@login_required
@admin_required
def search_machines():
    search_query = request.args.get('search', '')
    machines = Machine.query.filter(
        (Machine.name.ilike(f'%{search_query}%')) | 
        (Machine.ip.ilike(f'%{search_query}%')) |
        (Machine.mac.ilike(f'%{search_query}%'))
    ).all()
    
    return render_template('machines/table_contents.html', machines=machines)

@machines.route('/machines/<int:machineId>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def update_machine(machineId):
    # Update machine data.
    if request.method == 'PUT':
        machine = Machine.query.filter_by(id=machineId).first()
        if machine:
            updatedName = request.form.get('name')
            updatedMac = request.form.get('mac')
            updatedIp = request.form.get('ip')
            updatedPort = request.form.get('port')
            
            if updatedName == None:
                return flash('Name is required.', category='error'), 400
                
            if updatedMac == None:
                return flash('MAC address is required.', category='error'), 400

            if updatedIp == None:
                return flash('IP address is required.', category='error'), 400

            if updatedPort == None:
                return flash('Port is required.', category='error'), 400

            ipRegex = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            macRegex = r'(?:[0-9a-fA-F]){12}'
            macFullRegex = r'(?:[0-9a-fA-F]:?){12}'
            portRegex = r'^(0|[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$'

            if not (re.fullmatch(macRegex, updatedMac)) and not (re.fullmatch(macFullRegex, updatedMac)):
                return flash('MAC address is not valid.', category='error'), 400

            if (re.fullmatch(macRegex, updatedMac)):
                updatedMac = list(updatedMac)
                updatedMac.insert(10 ,':')
                updatedMac.insert(8 ,':')
                updatedMac.insert(6 ,':')
                updatedMac.insert(4 ,':')
                updatedMac.insert(2 ,':')
                updatedMac = ''.join(updatedMac)

            if not (re.fullmatch(ipRegex, updatedIp)):
                return flash('IP address is not valid.', category='error'), 400

            if not (re.fullmatch(portRegex, updatedPort)):
                return flash('Port is not valid.', category='error'), 400
                        
            try:
                machine.name = updatedName
                machine.mac = updatedMac
                machine.ip = updatedIp
                machine.port = updatedPort
                db_session.commit()
                return render_template('machines/row.html', machine=machine), 200
            except:
                return flash('Error updating machine data.', category='error'), 500
        else:
            return flash('Machine not found.', category='error'), 404
    
    # Remove machine.
    elif request.method == 'DELETE':
        machine = Machine.query.filter_by(id=machineId).first()
        if machine:
            try:
                db_session.delete(machine)
                db_session.commit()
                flash('Machine deleted successfully.', category='success')
                return ('', 200)
            except:
                return flash('Cannot delete machine.', category='error'), 500
        else:
            return flash('Machine not found.', category='error'), 404
