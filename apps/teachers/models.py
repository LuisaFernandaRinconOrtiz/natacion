from flask_login import UserMixin
from apps import mongo
from bson import ObjectId, errors

class Teachers(UserMixin):
    def __init__(self, first_name, second_name, first_last_name, second_last_name, dni, phone, experience):
        self.first_name = first_name
        self.second_name = second_name
        self.first_last_name = first_last_name
        self.second_last_name = second_last_name
        self.dni = dni  # Puede ser DNI o cédula
        self.state = True  # Activo por defecto
        self.phone = phone
        self.experience_years = int(experience or 0) # Años de experiencia

    def save(self):
        """Guarda el profesor en MongoDB"""
        mongo.db.teachers.insert_one(self.__dict__)

    @staticmethod
    def find_by_phone(phone):
        """Busca un profesor por teléfono"""
        return mongo.db.teachers.find_one({"phone": phone})

    @staticmethod
    def find_all():
        """Devuelve todos los profesores"""
        return list(mongo.db.teachers.find())

    @staticmethod
    def update_teacher(teacher_id, data):
        """Actualiza un profesor por su ID"""
        mongo.db.teachers.update_one({"_id": ObjectId(teacher_id)}, {"$set": data})

    @staticmethod
    def delete_teacher(teacher_id):
        """Elimina un profesor por su ID"""
        mongo.db.teachers.delete_one({"_id": ObjectId(teacher_id)})

    @staticmethod
    def get_teachers():
        """Obtiene todos los profesores activos con información básica"""
        projection = {
            '_id': 1,
            'first_name': 1,
            'second_name': 1,
            'first_last_name': 1,
            'second_last_name': 1,
            'dni': 1,
            'phone': 1,
            'experience_years': 1,
            'state': 1
        }

        # Buscar profesores activos (state=True) con los campos necesarios
        teachers = list(mongo.db.teachers.find({"state": True}, projection))

        # Formatear los resultados
        formatted_teachers = []
        for teacher in teachers:
            formatted_teachers.append({
                '_id': str(teacher['_id']),
                'name': f"{teacher.get('first_name', '')} {teacher.get('second_name', '')} {teacher.get('first_last_name', '')} {teacher.get('second_last_name', '')}".replace('  ', ' ').strip(),
                'dni': teacher.get('dni', ''),
                'phone': teacher.get('phone', ''),
                'experience': teacher.get('experience_years', 0),
                'label': f"{teacher.get('first_name', '')} {teacher.get('first_last_name', '')} ({teacher.get('experience_years', 0)} años exp.)"
            })

        return formatted_teachers

    @staticmethod
    def get_by_id(teacher_id):
        """Obtiene un profesor por su ID"""
        try:
            teacher = mongo.db.teachers.find_one({"_id": ObjectId(teacher_id)})
            if teacher:
                teacher['_id'] = str(teacher['_id'])  # Convertir ObjectId a string
            return teacher
        except errors.InvalidId:
            return None

# ✅ Crear índices en MongoDB para mejorar el rendimiento de las búsquedas
mongo.db.teachers.create_index("dni", unique=True)  # Asegurar que los DNI sean únicos
mongo.db.teachers.create_index("phone", unique=True)  # Asegurar que los teléfonos sean únicos
mongo.db.teachers.create_index("state")  # Optimizar la búsqueda de profesores activos
