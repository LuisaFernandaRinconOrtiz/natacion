from flask_login import UserMixin
from apps import mongo
from apps.authentication.util import hash_pass
from bson import ObjectId, errors

class Clients(UserMixin):
    def __init__(self, first_name, second_name, first_last_name, second_last_name, dni, addres, phone, email, age, medicall_info):
        self.first_name = first_name
        self.second_name = second_name
        self.first_last_name = first_last_name
        self.second_last_name = second_last_name
        self.dni = dni
        self.state = True  # Estado del cliente (activo por defecto)
        self.addres = addres
        self.phone = phone
        self.email = email
        self.age = age
        self.medicall_info = medicall_info

    def save(self):
        """Guarda el cliente en MongoDB"""
        mongo.db.clients.insert_one(self.__dict__)

    @staticmethod
    def get_by_id(client_id):
        """Obtiene un cliente por su ID"""
        try:
            client = mongo.db.clients.find_one({"_id": ObjectId(client_id)})
            if client:
                client['_id'] = str(client['_id'])  # Convertir ObjectId a string
            return client
        except errors.InvalidId:
            return None

    @staticmethod
    def find_by_email(email):
        """Busca un cliente por email"""
        return mongo.db.clients.find_one({"email": email})

    @staticmethod
    def find_all():
        """Devuelve todos los clientes"""
        return list(mongo.db.clients.find())

    @staticmethod
    def update_client(client_id, data):
        """Actualiza un cliente por su ID"""
        mongo.db.clients.update_one({"_id": ObjectId(client_id)}, {"$set": data})

    @staticmethod
    def delete_client(client_id):
        """Elimina un cliente por su ID"""
        mongo.db.clients.delete_one({"_id": ObjectId(client_id)})

    @staticmethod
    def get_students():
        """Obtiene todos los estudiantes (clientes) activos con solo información básica"""
        projection = {
            '_id': 1,
            'first_name': 1,
            'second_name': 1,
            'first_last_name': 1,
            'second_last_name': 1,
            'dni': 1,
            'phone': 1,
            'email': 1,
            'state': 1
        }

        # Buscar clientes activos (state=True) y proyectar solo los campos necesarios
        students = list(mongo.db.clients.find({"state": True}, projection))

        # Formatear los resultados para incluir nombre completo y datos relevantes
        formatted_students = []
        for student in students:
            formatted_students.append({
                '_id': str(student['_id']),
                'name': f"{student.get('first_name', '')} {student.get('second_name', '')} {student.get('first_last_name', '')} {student.get('second_last_name', '')}".replace('  ', ' ').strip(),
                'dni': student.get('dni', ''),
                'phone': student.get('phone', ''),
                'email': student.get('email', '')
            })

        return formatted_students

# ✅ Crear índices en MongoDB para mejorar el rendimiento de las búsquedas
mongo.db.clients.create_index("email", unique=True)  # Asegurar que los emails sean únicos
mongo.db.clients.create_index("dni", unique=True)  # Asegurar que los DNI sean únicos
mongo.db.clients.create_index("state")  # Optimizar la búsqueda de clientes activos
