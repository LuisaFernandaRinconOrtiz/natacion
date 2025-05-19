from apps.classes import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from bson import ObjectId, errors
from apps import mongo
from apps.classes.models import SwimmingClass
from apps.authentication.models import Users  # Asumiendo que tienes este modelo para usuarios
from apps.teachers.models import Teachers  # Asumiendo que tienes este modelo para usuarios
from apps.clients.models import Clients  # Asumiendo que tienes este modelo para usuarios

@blueprint.route('/list_classes')
@login_required
def list_classes():
    """Renderiza la página del calendario de clases."""
    return render_template('classes/calendar_classes.html', segment='clases')

@blueprint.route("/dataClasses", methods=["GET"])
@login_required
def dataClasses():
    """Obtiene todas las clases de natación en formato JSON para FullCalendar."""
    classes = SwimmingClass.find_all()
    
    events = []
    for cls in classes:
        # Obtener información del estudiante e instructor
        student = Clients.get_by_id(ObjectId(cls['student_id']))
        teacher = Teachers.get_by_id(ObjectId(cls['teacher_id']))
        
        for schedule in cls.get('schedule', []):
            events.append({
                'id': str(cls['_id']),
                'title': f"Clase con {student['first_name'] if student else 'Estudiante'}",
                'start': schedule,
                'extendedProps': {
                    'teacher': teacher['first_name'] if teacher else 'Instructor',
                    'state': cls.get('state', 'pendiente')
                },
                'className': f"fc-event-{cls.get('state', 'pendiente')}"
            })
    
    return jsonify(events)

@blueprint.route('/get_students', methods=['GET'])
@login_required
def get_students():
    """Obtiene la lista de estudiantes (clientes) activos."""
    
    try:
        students = Clients.get_students()
        return jsonify(students)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@blueprint.route('/get_teachers', methods=['GET'])
@login_required
def get_teachers():
    """Obtiene la lista de profesores activos."""
    try:
        teachers = Teachers.get_teachers()
        return jsonify(teachers)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@blueprint.route('/create_class', methods=['POST'])
@login_required
def create_class():
    """Crea una nueva clase de natación."""
    data = request.get_json()
    
    # Validación de datos
    if not data.get('student_id') or not data.get('teacher_id') or not data.get('schedule'):
        return jsonify({'success': False, 'message': 'Faltan datos obligatorios'}), 400
    
    try:
        # Convertir IDs a ObjectId
        class_data = {
            'student_id': ObjectId(data['student_id']),
            'teacher_id': ObjectId(data['teacher_id']),
            'schedule': data['schedule'] if isinstance(data['schedule'], list) else [data['schedule']],
            'state': data.get('state', 'pendiente')
        }
        
        swimming_class = SwimmingClass(**class_data)
        saved_class = swimming_class.save()  # Ahora devuelve el objeto con _id
        
        return jsonify({
            'success': True,
            'message': 'Clase creada correctamente',
            'id': str(saved_class._id)  # Usar _id en lugar de id
        })
        
    except errors.InvalidId:
        return jsonify({'success': False, 'message': 'ID no válido'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@blueprint.route('/get_class/<id>', methods=['GET'])
@login_required
def get_class(id):
    """Obtiene los detalles de una clase específica."""
    try:
        swimming_class = SwimmingClass.find_by_id(id)
        if not swimming_class:
            return jsonify({'success': False, 'message': 'Clase no encontrada'}), 404
            
        # Obtener información del estudiante e instructor
        student = Clients.get_by_id(swimming_class['student_id'])
        teacher = Teachers.get_by_id(swimming_class['teacher_id'])
        
        response = {
            '_id': str(swimming_class['_id']),
            'student_id': str(swimming_class['student_id']),
            'student_name': student['first_name'] if student else '',
            'teacher_id': str(swimming_class['teacher_id']),
            'teacher_name': teacher['first_name'] if teacher else '',
            'schedule': swimming_class.get('schedule', []),
            'state': swimming_class.get('state', 'pendiente')
        }
        
        return jsonify(response)
    except errors.InvalidId:
        return jsonify({'success': False, 'message': 'ID no válido'}), 400

@blueprint.route('/update_class', methods=['POST'])
@login_required
def update_class():
    """Actualiza una clase de natación existente."""
    data = request.get_json()
    class_id = data.pop('id', None)
    
    if not class_id:
        return jsonify({'success': False, 'message': 'ID no proporcionado'}), 400
    
    # Preparar datos para actualización
    update_data = {}
    if 'student_id' in data:
        update_data['student_id'] = ObjectId(data['student_id'])
    if 'teacher_id' in data:
        update_data['teacher_id'] = ObjectId(data['teacher_id'])
    if 'schedule' in data:
        update_data['schedule'] = data['schedule'] if isinstance(data['schedule'], list) else [data['schedule']]
    if 'state' in data:
        update_data['state'] = data['state']
    
    try:
        SwimmingClass.update_class(ObjectId(class_id), update_data)
        return jsonify({'success': True, 'message': 'Clase actualizada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@blueprint.route('/delete_class/<id>', methods=['DELETE'])
@login_required
def delete_class(id):
    """Elimina una clase de natación."""
    try:
        result = SwimmingClass.delete_class(ObjectId(id))
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Clase no encontrada'}), 404
        return jsonify({'success': True, 'message': 'Clase eliminada correctamente'})
    except errors.InvalidId:
        return jsonify({'success': False, 'message': 'ID no válido'}), 400