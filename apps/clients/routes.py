from apps.clients import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from bson import ObjectId
from apps import mongo
from apps.clients.models import Clients
from cerberus import Validator

def traducir_errores(errors):
    mensajes = []

    for campo, errores_campo in errors.items():
        for error in errores_campo:
            if "min length" in error:
                mensajes.append(f"'{campo}' debe tener al menos {error.split()[-1]} caracteres.")
            elif "regex" in error:
                if campo == 'phone' or campo == 'dni':
                    mensajes.append(f"'{campo}' solo debe contener números.")
                elif campo == 'email':
                    mensajes.append(f"'{campo}' debe ser un correo electrónico válido.")
                else:
                    mensajes.append(f"'{campo}' tiene un formato inválido.")
            elif "required field" in error:
                mensajes.append(f"El campo '{campo}' es obligatorio.")
            elif "empty values not allowed" in error:
                mensajes.append(f"El campo '{campo}' no puede estar vacío.")
            elif "min value" in error:
                mensajes.append(f"'{campo}' debe ser mayor o igual a {error.split()[-1]}.")
            else:
                mensajes.append(f"Error en el campo '{campo}': {error}")

    return mensajes

client_schema = {
    'first_name': {
        'type': 'string', 'minlength': 2, 'required': True, 'empty': False,
    },
    'second_name': {
        'type': 'string', 'minlength': 0, 'required': False,
    },
    'first_last_name': {
        'type': 'string', 'minlength': 2, 'required': True, 'empty': False,
    },
    'second_last_name': {
        'type': 'string', 'minlength': 0, 'required': False,
    },
    'dni': {
        'type': 'string', 'regex': '^[0-9]+$', 'required': False, 'empty': True,
    },
    'addres': {
        'type': 'string', 'minlength': 3, 'required': False,
    },
    'phone': {
        'type': 'string', 'minlength': 7, 'regex': '^[0-9]+$', 'required': True, 'empty': False,
    },
    'email': {
        'type': 'string', 'regex': r'^\S+@\S+\.\S+$', 'required': True, 'empty': False,
    },
    "age": {"nullable": True, "required": False},

    'medicall_info': {
        'type': 'string', 'required': False,
    },
}

@blueprint.route('/list_clients')
@login_required
def list_clients():
    return render_template('clients/list_clients.html',segment='estudiante')

@blueprint.route("/dataClients", methods=["GET"])
@login_required
def dataClients():
    clients = Clients.find_all()

    data_json = [
        {
            'id': str(item["_id"]),
            'names': item['first_name'] + " " + item['second_name'],
            'surnames': item['first_last_name'] + " " + item['second_last_name'],
            'document': item['dni'],
            'age': item['age'],
            'addres': item['addres'],
            'phone': item['phone'],
            'state': 'activado' if item['state'] else 'desactivado',
            'medicall_info': item['medicall_info'],
            'email': item['email'],
        } for item in clients
    ]

    return jsonify({'data': data_json})


@blueprint.route('/create_client', methods=['POST'])
@login_required
def create_client():
    data = request.get_json()

    # Validar si existe cliente con el mismo email
    existing_client_email = Clients.find_by_email(data.get('email'))
    if existing_client_email:
        return jsonify({'tipo': "error", 'message': 'Ya existe un cliente con ese email'}), 400

    # Validar si existe cliente con el mismo dni
    dni = data.get('dni')
    if dni:
        existing_client_dni = mongo.db.clients.find_one({'dni': dni})
        if existing_client_dni:
            return jsonify({'tipo': "error", 'message': 'Ya existe un cliente con esa identificación (DNI)'}), 400

    client = Clients(**data)
    client.save()

    return jsonify({'tipo': "success", 'message': 'Cliente creado correctamente'}), 200



@blueprint.route('/get_customer/<id>', methods=['GET'])
@login_required
def get_customer(id):
    client = mongo.db.clients.find_one({"_id": ObjectId(id)})

    if client:
        client["_id"] = str(client["_id"])  # Convertir ObjectId a string
        return jsonify(client)

    return jsonify({'error': 'Cliente no encontrado'}), 404

@blueprint.route('/edit_customer', methods=['POST'])
@login_required
def edit_customer():
    data = request.get_json()
    client_id = data.pop("id", None)

    if not client_id:
        return jsonify({'tipo': 'error', 'message': 'ID no proporcionado'}), 400

    # Validación parcial (no requiere todos los campos)
    partial_schema = {key: {**value, 'required': False} for key, value in client_schema.items()}
    v = Validator(partial_schema)
    if not v.validate(data):
        errores = traducir_errores(v.errors)
        return jsonify({'tipo': 'error', 'message': 'Datos inválidos', 'errores': errores}), 400

    Clients.update_client(ObjectId(client_id), data)

    return jsonify({'tipo': 'success', 'message': 'Cliente actualizado correctamente'})


@blueprint.route('/edit_state_client', methods=['POST'])
@login_required
def edit_state_client():
    try:
        data = request.form
        client_id = data.get('id')
        state = data.get('state')

        if not client_id or state not in ["0", "1"]:
            return jsonify({'tipo': 'error', 'message': 'Datos inválidos'}), 400

        state_value = True if state == "1" else False
        Clients.update_client(ObjectId(client_id), {"state": state_value})

        return jsonify({'tipo': 'success', 'message': f"Cliente {'activado' if state_value else 'desactivado'} correctamente"})
    
    except Exception as e:
        return jsonify({'tipo': 'error', 'message': str(e)}), 400


