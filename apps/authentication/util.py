def hash_pass(password):
    """Devuelve la contraseña en texto plano (no seguro)."""
    return password  # Se guarda tal cual

def verify_pass(password, stored_password):
    """Compara la contraseña en texto plano."""
    return password == stored_password  # Comparación directa
