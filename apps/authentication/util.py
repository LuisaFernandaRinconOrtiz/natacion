import bcrypt

def hash_pass(password):
    """Genera un hash seguro a partir de la contraseña."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_pass(password, stored_password):
    """Verifica que la contraseña ingresada coincide con el hash guardado."""
    return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
