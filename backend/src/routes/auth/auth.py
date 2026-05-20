from flask import Flask, Blueprint, jsonify, request
import mysql.connector
import src.routes.auth.auth_db as auth_db
import src.utils.seguridad as seguridad
import src.utils.errors as errors

auth_bp = Blueprint("auth",__name__)

@auth_bp.route("/", methods = ["POST"])
def login():
    data = request.get_json()

    if not data or "padron" not in data or "contrasena" not in data:
        return errors.datos_incompletos()
        
    padron = data["padron"]
    contrasena = data["contrasena"]

    usuario, error= auth_db.login_user(padron, contrasena)

    if error:
        return error

    token = seguridad.generar_token(usuario)
    return jsonify({'success': True, 'token': token}), 200
