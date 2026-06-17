from flask import Blueprint, jsonify, request, send_file
from mysql.connector import Error
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from src.db.db import obtener_alumno_por_padron, get_asistencia_padron, get_asistencias_curso
from src.utils.asistencia_utils import existe_padron, verificar_token, alumno_asistio, registrar_asistencia, hacer_y_guardar_qr, validar_padron, obtener_curso_por_codigo
from src.utils.errors import forbidden, error_response, bad_request, not_found, server_error, conflict
import config
from datetime import date,datetime

serializer = URLSafeTimedSerializer(config.SECRET_KEY)

asistencias_bp = Blueprint("asistencias",__name__)

@asistencias_bp.route('', methods=['GET'])
def asistencia(idCurso):

    try:
        #if not(verificar_token(request.headers, roles_permitidos=["Docente"])):
          #     return forbidden()     
        asistencia = get_asistencias_curso(idCurso)
        if len(asistencia) == 0:
            return "",204
        
        return jsonify(asistencia),200

    except Error as e:
       server_error(e)
    
@asistencias_bp.route('/<int:padron>', methods=['GET'])
def asistencia_id(padron, idCurso):

    try:
        #if not(verificar_token(request.headers, roles_permitidos=["Docente"])):
         #      return forbidden()

        if not(validar_padron(padron)):
            return bad_request("Padron invalido")
        asistencia = get_asistencia_padron(padron, idCurso)
        if len(asistencia) == 0:
            return "",204
        
        return jsonify(asistencia),200

    except Error as e:
        return server_error(e)
    
# accedido por el boton de "generar qr en /asistencia/profe
@asistencias_bp.route("/generar-qr", methods=["GET"])
def generar_qr(idCurso):
    try:
        payload = {"tipo": "asistencia", "timestamp": date.today().isoformat()}
        token = serializer.dumps(payload, salt="asistencia-qr")

        formulario_url = f"{config.FRONT_URL}/profesor/cursos/{idCurso}/asistencias/formulario?token={token}"

        hacer_y_guardar_qr(formulario_url)

        return {
        "mensaje": "QR generado exitosamente",
        "url_qr": formulario_url
        }, 202

    except Exception as e:
        return server_error(str(e))

@asistencias_bp.route("/confirmar-asistencia", methods=["POST"])
def confirmar_asistencia(idCurso):
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
    elif not registrar_asistencia(alumno["padron"], idCurso):
        return server_error("no se pudo registrar la asistencia")

    return {
        "mensaje": f"Asistencia registrada correctamente para {alumno['nombres']}",
        "alumno": alumno["nombres"],
        "curso": idCurso,
        "padron": alumno["padron"],
        "fecha": date.today().isoformat()
    }, 200

@asistencias_bp.route('/qr-imagen', methods=['GET'])
def servir_qr(idCurso):
    return send_file(config.QR_PATH, mimetype='image/png')
