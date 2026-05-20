from datetime import datetime, timedelta, timezone
import bcrypt
import jwt

SECRET_KEY = "ids2026_puntoycoma"

def generar_token(usuario):
    payload = {
        'iat': datetime.now(tz=timezone.utc),
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=4),
        'padron': usuario["padron"],
        'rol': usuario["rol"]
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(headers):
    #falta implementar con rol Docente
    return False

def hashear_contrasena(contrasena):
    hashear_contrasena = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
    return hashear_contrasena

def comparar_contrasena(contrasena, contrasena_hash):
    return bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash.encode('utf-8'))
