from flask import Blueprint, request, render_template, flash
from flask_login import login_required

import ping3, wakeonlan

from models import Machine

ping3.EXCEPTIONS = True

api = Blueprint('api', __name__)

@api.route('/api/wol/<int:machineId>', methods=['PUT'])
@login_required
def wol(machineId):
    machine = Machine.query.get(machineId)
    
    wakeonlan.wake(machine.mac, host=machine.ip , port=machine.port)

    if (request.headers.get('HX-Request') == 'true'):
        return render_template('wol_button.html', machine=machine, status=True)
    else:
        return '', 204

@api.route('/api/ping/<int:machineId>', methods=['GET'])
@login_required
def ping(machineId):
    machine = Machine.query.get(int(machineId))
    try:
        ping3.ping(machine.ip)
        
        if (request.headers.get('HX-Request') == 'true'):
            return render_template('ping_button.html', machine=machine, status=True)
        return '', 200
    
    except:
        if (request.headers.get('HX-Request') == 'true'):
            return render_template('ping_button.html', machine=machine, status=False)
        return '', 404