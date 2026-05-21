# Archivo temporal para generar tokens JWT de prueba

import jwt
import datetime

SECRET_KEY = "ids2026_puntoycoma"

payload = {
    "padron": 100000,
    "rol": "docente",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print(token)