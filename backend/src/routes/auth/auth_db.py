import mysql.connector
from db import get_connection
import src.utils.errors as errors

def login_user(padron, contrasena):
    #falta implementación de hash a la contraseña

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Usuarios where padron=%s", (padron,))
        usuario_logueado = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception:
        return None, errors.server_error()

    if not usuario_logueado:
        return None, errors.no_registrado(padron)

    if contrasena != usuario_logueado["contrasena_hash"]:
        return None, errors.contrasena_incorrecta()

    return usuario_logueado, None



