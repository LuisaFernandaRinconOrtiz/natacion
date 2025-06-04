# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from bson import ObjectId
from apps import mongo, login_manager
from apps.authentication.util import hash_pass

class Users(UserMixin):
    def __init__(self, username, password, _id=None, already_hashed=False):
        self.id = str(_id) if _id else None
        self.username = username
        self.password = password if already_hashed else hash_pass(password)

    def save(self):
        """ Guarda un usuario en MongoDB """
        user_data = {
            "username": self.username,
            "password": self.password
        }
        if self.id:
            mongo.db.users.update_one({"_id": ObjectId(self.id)}, {"$set": user_data})
        else:
            result = mongo.db.users.insert_one(user_data)
            self.id = str(result.inserted_id)

    def delete_from_db(self):
        """ Elimina el usuario de la base de datos """
        if self.id:
            mongo.db.users.delete_one({"_id": ObjectId(self.id)})

    @classmethod
    def find_by_username(cls, username):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return cls(user_data["username"], user_data["password"], _id=user_data["_id"], already_hashed=True)
        return None

    @classmethod
    def find_by_id(cls, _id):
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(_id)})
            if user_data:
                return cls(user_data["username"], user_data["password"], _id=user_data["_id"], already_hashed=True)
        except Exception:
            return None
        return None


    def __repr__(self):
        return str(self.username)

# ✅ Crear índice en username para acelerar búsquedas y evitar duplicados
mongo.db.users.create_index("username", unique=True)

@login_manager.user_loader
def user_loader(user_id):
    """ Carga un usuario por ID para Flask-Login """
    return Users.find_by_id(user_id)

@login_manager.request_loader
def request_loader(request):
    """ Carga un usuario desde una petición """
    username = request.form.get('username')
    return Users.find_by_username(username)
