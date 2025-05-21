from apps.clients import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from bson import ObjectId
from apps import mongo
from apps.clients.models import Clients

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

    existing_client = Clients.find_by_email(data.get('email'))
    if existing_client:
        return jsonify({'tipo': "error", 'message': 'Ya existe un cliente con ese email'}), 400

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

    Clients.update_client(ObjectId(client_id), data)

    return jsonify({'success': True, 'message': 'Cliente actualizado correctamente'})

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


