from flask import Flask, Blueprint, jsonify, request
import mysql.connector
import src.routes.auth.auth_db as auth_db
import src.utils.seguridad as seguridad
import src.utils.errors as errors
from src.utils.validaciones import es_email_valido

auth_bp = Blueprint("auth",__name__)




@auth_bp.route("/verificar_token", methods=["GET"])
def verificar_token():
    token = request.args.get("token")

    if not token:
        return errors.datos_incompletos()

    try:
        jwt.decode(
            token,
            seguridad.SECRET_KEY,
            algorithms = ["HS256"]
        )

        return jsonify({
            "code": "200",
            "message": "OK",
            "success": True,
            "description": "Token válido"
        }), 200

    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidSignatureError,
        jwt.InvalidTokenError
    ):
        return errors.acceso_denegado()



@auth_bp.route("/resetear-contrasena", methods=["PATCH"])
def resetear_token():
    data = request.get_json(silent=True)

    if not data or "token" not in data or "contrasena" not in data:
        return errors.datos_incompletos()

    token = data["token"]
    nueva_contrasena = data["contrasena"]

    try:
        payload = jwt.decode(
            token,
            seguridad.SECRET_KEY,
            algorithms = ["HS256"]
        )

    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        jwt.InvalidSignatureError,
    ):

        return errors.acceso_denegado()

    padron = payload["padron"]

    contrasena_hash = seguridad.hashear_contrasena(
        nueva_contrasena

    )

    resultado = auth_db.actualizar_contrasena(
        padron,
        contrasena_hash
    )

    if resultado:
        return resultado

    return jsonify({
        "code":"200",
        "message":"OK",
        "success": True,
        "description": "Contraseña reseteada correctamente"
    }), 200