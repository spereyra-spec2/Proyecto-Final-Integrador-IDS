from flask import Blueprint, jsonify, request, send_file
from mysql.connector import Error
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from src.db.db import obtener_alumno_por_padron, get_asistencia_id, get_asistencia
from src.utils.asistencia_utils import alumno_asistio, registrar_asistencia, hacer_y_guardar_qr
from src.utils.errors import error_response, bad_request, not_found, server_error, conflict
import config
from datetime import date
import os

serializer = URLSafeTimedSerializer(config.SECRET_KEY)

asistencia_bp = Blueprint("asistencia",__name__)

@asistencia_bp.route('', methods=['GET'])
def asistencia():

    try:
        asistencia = get_asistencia()
        if len(asistencia) == 0:
            return jsonify("insertar mensaje codigo 204"), 204

        return jsonify(asistencia),200

    except Error as e:
        error_payload= "insertar mensaje codigo 500"

        return jsonify(error_payload),500


@asistencia_bp.route('/<int:id>', methods=['GET'])
def asistencia_id(id):

    try:
        #funcion de validación de este id!!!

        asistencia = get_asistencia_id(id)
        if len(asistencia) == 0:
            return jsonify("insertar mensaje codigo 204"),204

        return jsonify(asistencia),200

    except Error as e:
        error_payload= "insertar mensaje codigo 500"

        return jsonify(error_payload),500


# accedido por el boton de "generar qr en /asistencia/profe
@asistencia_bp.route("/generar-qr", methods=["GET"])
def generar_qr():
    try:
        payload = {"tipo": "asistencia", "timestamp": date.today().isoformat()}
        token = serializer.dumps(payload, salt="asistencia-qr")

        base_url = config.BACK_URL
        formulario_url = f"{base_url}/api/asistencia/formulario-asistencia?token={token}"

        hacer_y_guardar_qr(formulario_url)

        return {
        "mensaje": "QR generado exitosamente",
        "url_qr": formulario_url
        }, 202

    except Exception as e:
        return server_error(str(e))

@asistencia_bp.route("/confirmar-asistencia", methods=["POST"])
def confirmar_asistencia():
    data = request.get_json(silent=True)
    if not data:
        return bad_request("El cuerpo debe ser JSON")

    padron = data.get("padron")
    token = data.get("token")

    if not padron:
        return bad_request("El padron es requerido")
    elif not token:
        return bad_request("No se incluyo el token")

    try:
        serializer.loads(token, salt="asistencia-qr", max_age=config.QR_EXPIRATION_SECONDS)
    except SignatureExpired:
        return error_response(401, "QR expirado", "error", "el codigo QR ha expirado, solicite uno nuevo al docente")
    except BadSignature:
        return error_response(403, "token invalido", "error", "el token enviado no es el valido")

    alumno = obtener_alumno_por_padron(padron)
    if not alumno:
        return not_found("no existe alumno con ese padron en la base de datos")
    elif alumno_asistio(alumno["padron"]):
        return conflict("ya has registrado tu asistencia hoy")
    elif not registrar_asistencia(alumno["padron"]):
        return server_error("no se pudo registrar la asistencia")

    return {
        "mensaje": f"Asistencia registrada correctamente para {alumno['nombres']}",
        "alumno": alumno["nombres"],
        "padron": alumno["padron"],
        "fecha": date.today().isoformat()
    }, 200

@asistencia_bp.route('/qr-imagen', methods=['GET'])
def servir_qr():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'backend', 'qr_asistencia.png')
    ruta = os.path.normpath(ruta)
    print("Buscando QR en:", ruta)
    return send_file(ruta, mimetype='image/png')
