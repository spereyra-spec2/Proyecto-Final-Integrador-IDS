from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from . import errors as errors
from flask_mail import Message
from mail import mail
from flask import current_app

SECRET_KEY = "ids2026_puntoycoma_super_seguro_#123abc456def"

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

            if payload['proposito'] != 'reset':
                return errors.acceso_denegado()

            roles = payload["rol"]

            if roles in roles_permitidos:
                return True
            return False
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            return False

    return False


def generar_token_contrasena(padron):
    payload = {
        'iat': datetime.now(tz=timezone.utc),
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=15),
        'padron': padron,
        'proposito': 'reset'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def enviar_mail_contrasena(destinatario, token):
    link = f"http://localhost:5001/api/auth/resetear_contrasena?token={token}" #despues cambiar cuando se integre front, solo es de prueba
    mensaje = Message(
        subject="Recuperación de Contraseña",
        sender= current_app.config['MAIL_USERNAME'],
        recipients=[destinatario]
    )
    mensaje.body = f"Hace click en este link para recuperar tu contraseña {link}. \n Recordá que solo es válido durante 15 minutos"

    try:
        mail.send(mensaje)
        return True, None
    except Exception as e:
        return None, errors.error_enviando_correo(e)