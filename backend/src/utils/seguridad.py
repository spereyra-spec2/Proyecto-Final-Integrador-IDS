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

def verificar_token(headers):
    if "Authorization" in headers.keys():
        authorization=headers["Authorization"]
        print(authorization)
        encoded_token=authorization.split(" ")[1]
        print(encoded_token)

        try:
            payload=jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
            roles = list(payload["rol"])

            if 'Docente' in roles:
                return True
            return False
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            return False

    return False

