from flask import Blueprint, request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from db import obtener_alumno_por_padron
from src.utils.asistencia_utils import alumno_asistio, ip_registrado, registrar_asistencia, hacer_y_guardar_qr
from src.utils.errors import error_response, bad_request, not_found, server_error, conflict
import config
from datetime import date
import os

asistencia_qr_bp = Blueprint("asistencia_qr", __name__)
serializer = URLSafeTimedSerializer(config.SECRET_KEY)

@asistencia_qr_bp.route("/generar-qr", methods=["POST"])
def generar_qr():
    try:
        payload = {"tipo": "asistencia", "timestamp": date.today().isoformat()}
        token = serializer.dumps(payload, salt="asistencia-qr")

        base_url = config.BASE_URL
        formulario_url = f"{base_url}/api/formulario-asistencia?token={token}"

        hacer_y_guardar_qr(formulario_url)

        return {
        "mensaje": "QR generado exitosamente",
        "url_qr": formulario_url
        }, 202

    except Exception as e:
        return server_error(str(e))

@asistencia_qr_bp.route("formulario-asistencia", methods=["GET"])
def formulario_asistencia():
    token = request.args.get("token")
    if not token:
        return bad_request("token no fue enviado")

    try:
        serializer.loads(token, salt="asistencia-qr", max_age=config.QR_EXPIRATION_SECONDS)
    except SignatureExpired:
        return "<h1> QR expirado </h1>", 401
    except BadSignature:
        return "<h1> token invalido </h1>", 403

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    template_path = os.path.join(base_dir, "frontend", "src", "templates", "formulario_asistencia.html")
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()
    except FileNotFoundError:
        print(f"no se encontró el template en: {template_path}")  # Para debug, BORRAR
        return "<h1>Error</h1><p>No se encontró el formulario</p>", 500

    html_content = html_template.replace("{{ token }}", token)
    return html_content, 200

@asistencia_qr_bp.route("/confirmar-asistencia", methods=["POST"])
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

    ip_adress = request.remote_addr
    if request.headers.get('X-Forwarded-For'):
        ip_adress = request.headers.get('X-Forwarded-For').split(',')[0]

    if ip_registrado(ip_adress):
        return conflict("solo esta permitido registrar una asistencia por IP, por cualquier problema avisar al docente")
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
    elif not registrar_asistencia(alumno["padron"], ip_adress):
        return server_error("no se pudo registrar la asistencia")

    return {
        "mensaje": f"Asistencia registrada correctamente para {alumno['nombres']}",
        "alumno": alumno["nombres"],
        "padron": alumno["padron"],
        "fecha": date.today().isoformat()
    }, 200
