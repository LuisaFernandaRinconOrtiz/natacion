from flask_login import UserMixin
from apps import mongo
from bson import ObjectId

class SwimmingClass(UserMixin):
    def __init__(self, student_id, teacher_id, schedule, state):
        """
        Clase de natación.
        :param student_id: ID del estudiante (debe existir en la base de datos).
        :param teacher_id: ID del profesor (debe existir en la base de datos).
        :param schedule: Lista de horarios [{'date': 'YYYY-MM-DD', 'time': 'HH:MM'}].
        :param state: Estado de la clase ('pendiente', 'completada', 'cancelada').
        """
        self.student_id = str(student_id)
        self.teacher_id = ObjectId(teacher_id)
        self.schedule = schedule  # Lista de fechas y horas
        self.state = state  # Estado de la clase

    def save(self):
        """Guarda la clase en MongoDB y retorna el objeto insertado con su ID."""
        result = mongo.db.swimming_classes.insert_one(self.__dict__)
        self._id = result.inserted_id  # Guardar el ID generado en la instancia
        return self  # Retornar la instancia con el _id asignado

    @staticmethod
    def find_by_id(class_id):
        """Encuentra una clase por su ID."""
        return mongo.db.swimming_classes.find_one({"_id": ObjectId(class_id)})

    @staticmethod
    def find_all():
        """Obtiene todas las clases de natación."""
        return list(mongo.db.swimming_classes.find())

    @staticmethod
    def find_by_student(student_id):
        """Encuentra clases de un estudiante específico."""
        return list(mongo.db.swimming_classes.find({"student_id": ObjectId(student_id)}))

    @staticmethod
    def find_by_teacher(teacher_id):
        """Encuentra clases asignadas a un profesor específico."""
        return list(mongo.db.swimming_classes.find({"teacher_id": ObjectId(teacher_id)}))

    @staticmethod
    def update_class(class_id, data):
        """Actualiza una clase de natación."""
        mongo.db.swimming_classes.update_one({"_id": ObjectId(class_id)}, {"$set": data})

    @staticmethod
    def add_schedule(class_id, new_schedule):
        """Añade más fechas y horas a una clase existente."""
        mongo.db.swimming_classes.update_one(
            {"_id": ObjectId(class_id)},
            {"$push": {"schedule": {"$each": new_schedule}}}
        )

    @staticmethod
    def delete_class(class_id):
        """Elimina una clase de natación y devuelve el resultado de la operación."""
        result = mongo.db.swimming_classes.delete_one({"_id": ObjectId(class_id)})
        return result  # Retornamos el resultado de la eliminación

# ✅ Crear índices en MongoDB para optimizar búsquedas
mongo.db.swimming_classes.create_index("student_id")  # Búsquedas rápidas por estudiante
mongo.db.swimming_classes.create_index("teacher_id")  # Búsquedas rápidas por profesor
