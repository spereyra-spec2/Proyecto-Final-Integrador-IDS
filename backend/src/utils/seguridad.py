from datetime import datetime, timedelta, timezone
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