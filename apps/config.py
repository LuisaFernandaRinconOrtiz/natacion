import os

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = '/static/assets' 
    
    # Set up the App SECRET_KEY
    SECRET_KEY  = 'zjyz0BAg3ZKp0HYDo0s2Y2WvZPtASXPs'

    # Configuración de MongoDB - Usar la IP de la máquina Windows
    MONGO_URI = 'mongodb://172.17.96.1:27017/natacion'

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    DEBUG = True

# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
