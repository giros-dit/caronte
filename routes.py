from flask import Blueprint, request, abort, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
import random
import string
import re
import os

from models import User, Machine, Ownership
from database import db_session
import mail.mail as mail
from app import config

routes = Blueprint('routes', __name__)


@routes.route('/machines', methods=['POST', 'PUT'])
@login_required
def machines():
    if current_user.admin:
        if request.method == 'PUT':

            ipRegex = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            macRegex = r'(?:[0-9a-fA-F]){12}'
            macFullRegex = r'(?:[0-9a-fA-F]:?){12}'
            portRegex = r'^(0|[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$'

            name = request.json['name'].strip()
            mac = request.json['mac'].strip()
            ip = request.json['ip'].strip()
            port = request.json['port'].strip()

            if (re.fullmatch(macRegex, mac)):
                mac = list(mac)
                mac.insert(10 ,':')
                mac.insert(8 ,':')
                mac.insert(6 ,':')
                mac.insert(4 ,':')
                mac.insert(2 ,':')
                mac = ''.join(mac)

            if os.environ.get('ENV') != "development":
                if (re.fullmatch(macFullRegex, mac)):
                    if (re.fullmatch(ipRegex, ip)):
                        if (re.fullmatch(portRegex, port)):
                            if Machine.query.filter_by(name = name, mac = mac, ip = ip, port = port).first():
                                response = {
                                    'code': 1,
                                    'message': "Ya existe una máquina con los mismos datos."
                                }

                            else:
                                try:
                                    new_machine = Machine(name, mac, ip, port)
                                    db_session.add(new_machine)
                                    db_session.commit()

                                    machine = Machine.query.filter_by(name = name, mac = mac, ip = ip, port = port).first()
                                    response = {
                                        'code': 0,
                                        'id': machine.id
                                    }

                                except:
                                    response = {
                                        'code': 2,
                                        'message': "Error al añadir la máquina a la base de datos."
                                    }

                        else:
                            response = {
                                'code': 5,
                                'message': "El puerto introducido no tiene un formato válido."
                            }

                    else:
                        response = {
                            'code': 4,
                            'message': "La dirección IP introducida no tiene un formato válido."
                        }

                else:
                    response = {
                        'code': 3,
                        'message': "La dirección MAC introducida no tiene un formato válido."
                    }

            else:
                try:
                    new_machine = Machine(name, mac, ip, port)
                    db_session.add(new_machine)
                    db_session.commit()
                    machine = Machine.query.filter_by(name = name, mac = mac, ip = ip, port = port).first()
                    response = {
                        'code': 0,
                        'id': machine.id
                    }

                except:
                    response = {
                        'code': 2,
                        'message': "Error al añadir la máquina a la base de datos."
                    }

            return response
          
    else:
        abort(403)


@routes.route('/machines/<int:machineId>', methods=['POST', 'DELETE'])
@login_required
def machine(machineId):
    if current_user.admin:
        if request.method == 'POST':
            update_machine = Machine.query.get(machineId)

            name = request.json['name']
            mac = request.json['mac']
            ip = request.json['ip']
            port = request.json['port']

            if Machine.query.filter_by(id=machineId).first():
                if not Machine.query.filter_by(name = name, mac = mac, ip = ip, port = port).first():
                    try:
                        update_machine.name = name
                        update_machine.mac = mac
                        update_machine.ip = ip
                        update_machine.port = port
                        db_session.commit()

                        response = {
                            'code': 0
                        }

                    except:
                        response = {
                            'code': 1,
                            'message': "Error al actualizar la máquina en la base de datos."
                        }

                else:
                    response = {
                        'code': 2,
                        'message': "Ya existe una máquina con los mismos datos."
                    }
            
            else:
                response = {
                    'code': 3,
                    'message': "La máquina especificada no existe."
                }

            return response
        
        elif request.method == 'DELETE':
            if Machine.query.filter_by(id=machineId).first():
                try:
                    db_session.delete(Machine.query.get(machineId))
                    db_session.commit()
                    response = {
                            'code': 0
                    }

                except:
                    response = {
                        'code': 1,
                        'message': "Error al eliminar la máquina de la base de datos."
                    }

            else:
                response = {
                    'code': 2,
                    'message': "La máquina especificada no existe."
                }
            
            return response
    else:
        abort(403)
        
