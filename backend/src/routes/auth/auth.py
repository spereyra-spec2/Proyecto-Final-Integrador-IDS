from flask import Flask, Blueprint, jsonify, request
import mysql.connector
import src.routes.auth.auth_db as auth_db
import src.utils.seguridad as seguridad
import src.utils.errors as errors
from src.utils.validaciones import es_email_valido
import jwt

auth_bp = Blueprint("auth",__name__)

@auth_bp.route("/login", methods = ["POST"])
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
    return jsonify({'success': True, 'token': token, 'padron': usuario['padron'], 'rol': usuario['rol']}), 200


@auth_bp.route("/registro", methods = ["POST"])
def alta_usuario():
    data = request.get_json(silent=True)

    if not data or "padron" not in data or "nombres" not in data or "mail" not in data or "contrasena" not in data:
        return errors.datos_incompletos()
    
    if not isinstance(data["padron"], int):
        return errors.datos_incorrectos("padron")
    
    if data["padron"] < 99999:
        return errors.datos_incorrectos("padron")
    
    if not isinstance(data["nombres"], str) or len(data["nombres"]) == 0:
        return errors.datos_incorrectos("nombres")
    
    if not es_email_valido(data["mail"]):
        return errors.datos_incorrectos("mail")
    
    if len(data["contrasena"]) < 8:
        return errors.datos_incorrectos("contraseña")
    
    existe_usuario, error = auth_db.existe_usuario(data["padron"])

    if existe_usuario:
        return errors.ya_existe()
    
    if error:
        return error
    
    resultado = auth_db.alta_usuario(data["padron"], "Docente", data["nombres"], data["mail"], data["contrasena"])

    if resultado:
        return resultado #si llega acá es porque tiró error
    
    return ("", 201)
    
'''
Ejemplo de implementación (BORRAR LUEGO)
@auth_bp.route("/prueba", methods = ["GET"])
def prueba():
    palabra = "hola"

    tiene_acceso = seguridad.verificar_token(request.headers, ["Docente"])
    
    if tiene_acceso:
        return jsonify({"palabra": palabra}), 200
    else:
        return jsonify({"error": "no autorizado"}), 401
'''

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

    except jwt.PyJWTError:
        return errors.acceso_denegado()


@auth_bp.route("/contrasena_olvidada", methods=["POST"])
def contrasena_olvidada():
    data = request.get_json(silent=True)

    if not data or "padron" not in data:
        return errors.datos_incompletos()
    
    usuario, error = auth_db.existe_usuario(data["padron"])

    if error:
        return error
    
    if not usuario:
        return errors.no_registrado(data["padron"])
    
    if usuario:
        mail_usuario, error_mail= auth_db.obtener_mail_usuario(data["padron"])

        if error_mail:
            return error_mail
        
        token_reset = seguridad.generar_token_contrasena(data["padron"])

        mail_enviado, error_enviando = seguridad.enviar_mail_contrasena(mail_usuario, token_reset)

        if error_enviando:
            return error_enviando
        
        return jsonify({'success': True}), 200
        

@auth_bp.route("/resetear_contrasena", methods=["PATCH"])
def resetear_contrasena():
    data = request.get_json(silent=True)
    token = request.args.get("token")

    if not "token" or "contrasena" not in data:
        return errors.datos_incompletos()

    nueva_contrasena = data["contrasena"]

    try:
        payload = jwt.decode(
            token.encode('utf-8'),
            seguridad.SECRET_KEY,
            algorithms = ["HS256"]
        )

    except jwt.PyJWTError as e:
        return errors.acceso_denegado()

    padron = payload["padron"]

    contrasena_hash = seguridad.hashear_contrasena(nueva_contrasena)

    resultado = auth_db.actualizar_contrasena(padron, contrasena_hash)

    if resultado:
        return resultado

    return jsonify({
        "code":"200",
        "message":"OK",
        "success": True,
        "description": "Contraseña actualizada correctamente."
    }), 200
