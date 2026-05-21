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

def hashear_contrasena(contrasena):
    hashear_contrasena = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
    return hashear_contrasena

def comparar_contrasena(contrasena, contrasena_hash):
    return bcrypt.checkpw(contrasena.encode('utf-8'), contrasena_hash.encode('utf-8'))


def verificar_token(headers, roles_permitidos):
    if "Authorization" in headers.keys():
        authorization=headers["Authorization"]
        encoded_token=authorization.split(" ")[1]

        try:
            payload=jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
            roles = payload["rol"]

            if roles in roles_permitidos:
                return True
            return False
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            return False

    return False

