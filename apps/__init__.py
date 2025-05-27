from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from importlib import import_module

# Inicializar extensiones
mongo = PyMongo()
login_manager = LoginManager()

def register_extensions(app):
    """Registra las extensiones de Flask"""
    app.config["MONGO_URI"] = app.config.get("MONGO_URI")
    mongo.init_app(app)  # 🔹 Inicia MongoDB
    login_manager.init_app(app)  # 🔹 Inicia Flask-Login
    
    # 🔹 Imprimir si MongoDB está listo
    with app.app_context():
        try:
            print("✅ MongoDB conectado, colecciones disponibles:", mongo.db.list_collection_names())
        except Exception as e:
            print("❌ Error al conectar con MongoDB:", e)

def register_blueprints(app):
    """Registra los Blueprints"""
    for module_name in ('authentication', 'home', 'clients','teachers','classes','index'):
        module = import_module(f'apps.{module_name}.routes')
        app.register_blueprint(module.blueprint)

def create_app(config):
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config)
    
    register_extensions(app)  # 🔹 Asegúrate de inicializar MongoDB primero
    register_blueprints(app)

    return app
