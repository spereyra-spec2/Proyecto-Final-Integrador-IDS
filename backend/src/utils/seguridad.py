from flask import Request
from typing import Any
import jwt

from config import SECRET_KEY
import src.utils.funciones as funciones

# Uso la misma lógica que la rama de Julieta
def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, funciones.unauthorized("Falta Authorization header"), 401

    parts = auth_header.split()

    if len(parts) != 2 or parts[0] != "Bearer":
        return None, funciones.unauthorized("Formato de Authorization header inválido. Se esperaba 'Bearer <token>'"), 401

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        return payload, None
    
    except jwt.ExpiredSignatureError:
        return None, funciones.unauthorized("Token expirado"), 401

    except jwt.InvalidTokenError:
        return None, funciones.unauthorized("Token inválido"), 401