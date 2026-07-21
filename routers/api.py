from flask import Blueprint, request, render_template, make_response, redirect, url_for
from flask_login import current_user
from auth import authentication_required, authorization_required

import json

import ping3, wakeonlan

from models import User, Machine, Ownership

ping3.EXCEPTIONS = True

api = Blueprint('api', __name__)

@api.route('/api/test', methods=['GET'])
@authentication_required
def test():
    response = make_response('', 200)
    
    if (request.headers.get('HX-Request') == 'true'):
        response.headers['HX-Trigger-After-Settle'] = '''{"new-toast": {"type": "success", "message": "Test successful!", "title": "Success", "options": {}}}'''
        
    return response

@api.route('/api/wol/<int:machineId>', methods=['GET'])
@authentication_required
@authorization_required
def wol(machineId):
    machine = Machine.query.get(machineId)
    
    wakeonlan.wake(machine.mac, host=machine.ip , port=machine.port)

    if (request.headers.get('HX-Request') == 'true'):
        response = make_response(render_template('buttons/wol.html', machine=machine, status=True), 200)
        toast = {"type": "success",
                 "message": f"Paquete enviado a {machine.name}",
                 "title": "Paquete WoL enviado",
                 "options": {}
                 }
        response.headers['HX-Trigger-After-Settle'] = '''{"new-toast": ''' + json.dumps(toast) + '''}'''
    else:
        response = make_response('', 200)
        
    return response


@api.route('/api/ping/<int:machineId>', methods=['GET'])
@authentication_required
@authorization_required
def ping(machineId):
    machine = Machine.query.get(int(machineId))
    
    try:
        ping3.ping(machine.ip)
        
        if (request.headers.get('HX-Request') == 'true'):
            response = make_response(render_template('buttons/ping.html', machine=machine, status=True), 200)
            toast = {"type": "success",
                     "message": f"{machine.name} responde a ping",
                     "title": "Máquina alcanzable",
                     "options": {}
                     }
            response.headers['HX-Trigger-After-Settle'] = '''{"new-toast": ''' + json.dumps(toast) + '''}'''
        else:
            response = make_response('', 200)
            
    
    except:
        if (request.headers.get('HX-Request') == 'true'):
            response = make_response(render_template('buttons/ping.html', machine=machine, status=False), 200)
            toast = {"type": "error",
                     "message": f"{machine.name} no responde a ping",
                     "title": "Máquina no alcanzable",
                     "options": {}
                     }
            response.headers['HX-Trigger-After-Settle'] = '''{"new-toast": ''' + json.dumps(toast) + '''}'''
        else:
            response = make_response('', 404)
    
    return response

@api.route('/api/machines/search', methods=['GET'])
@authentication_required
@authorization_required
def search_my_machines():
    search_query = request.args.get('search', '')
    
    user = current_user
    ownership = Ownership.query.filter_by(user_id=user.id).all()
    
    owned_machine_ids = [o.machine_id for o in ownership]
    
    machines = Machine.query.filter(Machine.id.in_(owned_machine_ids)).filter(
        (Machine.name.ilike(f'%{search_query}%')) | 
        (Machine.ip.ilike(f'%{search_query}%')) |
        (Machine.mac.ilike(f'%{search_query}%'))
    ).all()
    
    if (request.headers.get('HX-Request') == 'true'):
        response = make_response(render_template('index/table_contents.html', machines=machines), 200)
    else:
        response = make_response(json.dumps([machine.to_dict() for machine in machines]), 200)
    
    return response