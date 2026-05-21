from flask import Flask, Blueprint, jsonify, request
import mysql.connector
import src.routes.auth.auth_db as auth_db
import src.utils.seguridad as seguridad
import src.utils.errors as errors
from src.utils.validaciones import es_email_valido

auth_bp = Blueprint("auth",__name__)


@auth_bp.route("/verificar-token", methods=["GET"])
def verificar_token():
    token = request.args.get("token")

    if not token:
        return errors.datos_incompletos("token")

    try:
        jwt.decode(
            token,
            seguridad.SECRET_KEY,
            algorithms = ["HS256"]
        )
    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidSignatureError,
        jwt.InvalidTokenError
    ):
        return errors.acceso_denegado

    return jsonify({
        "success": True,
        "message": "Token válido",
    }), 200



@auth_bp.route("/resetear-contrasena", methods=["PATCH"])
def resetear_token():
    data = request.get_json(silent=True)

    if not data or "token" not in data or "contrasena" not in data:
        return errors.datos_incompletos("contrasena")

    token = data["token"]
    nueva_contrasena = data["contrasena"]

    try:
        payload = jwt.decode(
            data["token"],
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
        data["contrasena"]

    )

    resultado = auth_db.actualizar_contrasena(
        padron,
        contrasena_hash
    )

    if resultado:
        return resultado

    return ("",200)