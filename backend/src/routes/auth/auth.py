from flask import Flask, Blueprint, jsonify, request
import mysql.connector
import src.routes.auth.auth_db as auth_db
import src.utils.seguridad as seguridad
import src.utils.errors as errors
from src.utils.validaciones import es_email_valido

auth_bp = Blueprint("auth",__name__)

@auth_bp.route("/", methods = ["POST"])
def login():
    data = request.get_json(silent=True)

    if not data or "padron" not in data or "contrasena" not in data:
        return errors.datos_incompletos()
        
    padron = data["padron"]
    contrasena = data["contrasena"]

    usuario, error= auth_db.login_user(padron, contrasena)

    if error:
        return error

    token = seguridad.generar_token(usuario)
    return jsonify({'success': True, 'token': token}), 200


@auth_bp.route("/registro", methods = ["POST"])
def alta_usuario():
    data = request.get_json(silent=True)

    if not data or "padron" not in data or "rol" not in data or "nombres" not in data or "mail" not in data or "contrasena" not in data:
        return errors.datos_incompletos()
    
    if not isinstance(data["padron"], int):
        return errors.datos_incorrectos("padron")
    
    if not isinstance(data["nombres"], str) or len(data["nombres"]) == 0:
        return errors.datos_incorrectos("nombres")
    
    if not es_email_valido(data["mail"]):
        return errors.datos_incorrectos("mail")
    
    if len(data["contrasena"]) < 8:
        return errors.datos_incorrectos("contraseña")
    
    existe_usuario = auth_db.existe_usuario(data["padron"])

    if(existe_usuario):
        return errors.ya_existe_alumno()
    
    resultado = auth_db.alta_usuario(data["padron"], data["rol"], data["nombres"], data["mail"], data["contrasena"])

    if resultado:
        return resultado #si llega acá es porque tiró error
    
    return ("", 201)
    

