from apps.teachers import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from bson import ObjectId, errors
from apps import mongo
from apps.teachers.models import Teachers

@blueprint.route('/list_teachers')
@login_required
def list_teachers():
    return render_template('teachers/list_teachers.html', segment='profesor')

@blueprint.route("/dataTeachers", methods=["GET"])
@login_required
def dataTeachers():
    teachers = Teachers.find_all()

    data_json = [
        {
            'id': str(item["_id"]),
            'names': f"{item['first_name']} {item['second_name']}",
            'surnames': f"{item['first_last_name']} {item['second_last_name']}",
            'document': item['dni'],
            'phone': item['phone'],
            'state': 'activado' if item['state'] else 'desactivado',
            'experience_years': item.get('experience_years', 0),
        } for item in teachers
    ]

    return jsonify({'data': data_json})

@blueprint.route('/create_teacher', methods=['POST'])
@login_required
def create_teacher():
    data = request.get_json()

    existing_teacher = Teachers.find_by_phone(data.get('phone'))
    if existing_teacher:
        return jsonify({'tipo': "error", 'message': 'Ya existe un profesor con ese número de teléfono'}), 400

    teacher = Teachers(**data)
    teacher.save()

    return jsonify({'tipo': "success", 'message': 'Profesor creado correctamente'}), 200

@blueprint.route('/get_teacher/<id>', methods=['GET'])
@login_required
def get_teacher(id):
    try:
        teacher = mongo.db.teachers.find_one({"_id": ObjectId(id)})

        if teacher:
            teacher["_id"] = str(teacher["_id"])  # Convertir ObjectId a string
            return jsonify(teacher)

        return jsonify({'error': 'Profesor no encontrado'}), 404

    except errors.InvalidId:
        return jsonify({'error': 'ID no válido'}), 400

@blueprint.route('/edit_teacher', methods=['POST'])
@login_required
def edit_teacher():
    data = request.get_json()
    teacher_id = data.pop("id", None)

    if not teacher_id:
        return jsonify({'tipo': 'error', 'message': 'ID no proporcionado'}), 400

    try:
        Teachers.update_teacher(ObjectId(teacher_id), data)
        return jsonify({'success': True, 'message': 'Profesor actualizado correctamente'})
    except errors.InvalidId:
        return jsonify({'tipo': 'error', 'message': 'ID no válido'}), 400

@blueprint.route('/edit_state_teacher', methods=['POST'])
@login_required
def edit_state_teacher():
    try:
        data = request.form
        teacher_id = data.get('id')
        state = data.get('state')

        if not teacher_id or state not in ["0", "1"]:
            return jsonify({'tipo': 'error', 'message': 'Datos inválidos'}), 400

        state_value = True if state == "1" else False
        Teachers.update_teacher(ObjectId(teacher_id), {"state": state_value})

        return jsonify({'tipo': 'success', 'message': f"Profesor {'activado' if state_value else 'desactivado'} correctamente"})
    
    except Exception as e:
        print(e)
        return jsonify({'tipo': 'error', 'message': str(e)}), 400


@blueprint.route("/dataTeachersFiltered", methods=["POST"])
@login_required
def dataTeachersFiltered():
    filters = request.get_json() or {}
    pipeline = []

    # Si hay filtros de coincidencia
    # Filtra documentos que coinciden con una condición
    if "match" in filters and filters["match"]:
        pipeline.append({"$match": filters["match"]})
    # Ordena los documentos
    if "sort" in filters:
        pipeline.append({"$sort": filters["sort"]})
    # Omite los primeros N documentos
    if "skip" in filters:
        pipeline.append({"$skip": int(filters["skip"])})
    # Limita el número de documentos devueltos
    if "limit" in filters:
        pipeline.append({"$limit": int(filters["limit"])})
    # Selecciona los campos a devolver
    if "project" in filters:
        pipeline.append({"$project": filters["project"]})

    # Si no hay ningún filtro, usar todos los datos
    if not pipeline:
        teachers = Teachers.find_all()
    else:
        teachers = list(mongo.db.teachers.aggregate(pipeline))

    # Procesar para DataTable
    data_json = [
        {
            'id': str(item["_id"]),
            'names': f"{item.get('first_name', '')} {item.get('second_name', '')}",
            'surnames': f"{item.get('first_last_name', '')} {item.get('second_last_name', '')}",
            'document': item.get('dni', ''),
            'phone': item.get('phone', ''),
            'state': 'activado' if item.get('state', False) else 'desactivado',
            'experience_years': item.get('experience_years', 0),
        } for item in teachers
    ]

    return jsonify({'data': data_json})