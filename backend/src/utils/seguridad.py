from flask import Request
from typing import Any
import jwt
import src.utils.errors as errors

SECRET_KEY = "ids2026_puntoycoma_super_seguro_#123abc456def"

def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, errors.unauthorized("Falta Authorization header"), 401

    parts = auth_header.split()

    if len(parts) != 2 or parts[0] != "Bearer":
        return None, errors.unauthorized("Formato de Authorization header inválido. Se esperaba 'Bearer <token>'"), 401

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        return payload, None
    
    except jwt.ExpiredSignatureError:
        return None, errors.unauthorized("Token expirado"), 401

    except jwt.InvalidTokenError:
        return None, errors.unauthorized("Token inválido"), 401
