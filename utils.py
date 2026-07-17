from flask import make_response, redirect, url_for

import json

from models import User, Machine, Ownership


def getUser(userId):
    user = User.query.get(userId)
    if user:
        return user
    else:
        response = make_response('', 404)
        toast = {"type": "error",
                 "message": f"El usuario con ID {userId} no existe.",
                 "title": "Usuario no encontrado",
                 "options": {}
                }
        response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
        
        raise LookupError(response)

def getUserByToken(token):
    user = User.query.filter_by(recovery_token=token).first()
    if user:
        return user
    else:
        response = make_response(redirect(url_for('views.index')), 404)
        toast = {"type": "error",
                 "message": "Token inválido o expirado.",
                 "title": "Token no encontrado",
                 "options": {}
                }
        response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
        
        raise LookupError(response)

def getMachine(machineId):
    machine = Machine.query.get(machineId)
    if machine:
        return machine
    else:
        response = make_response('', 404)
        toast = {"type": "error",
                 "message": f"La máquina con ID {machineId} no existe.",
                 "title": "Máquina no encontrada",
                 "options": {}
                }
        response.headers['HX-Trigger-After-Settle'] = f'{{"new-toast": {json.dumps(toast)} }}'
        
        raise LookupError(response)