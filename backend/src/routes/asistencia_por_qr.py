from flask import Blueprint, request, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from db import obtener_alumno_por_padron, ya_usado_token, registrar_asistencia
from tasks import enviar_qr_async
from src.utils.errors import error_response, bad_request, not_found, server_error, conflict
import config
from datetime import date

asistencia_qr_bp = Blueprint("asistencia_qr", __name__)
serializer = URLSafeTimedSerializer(config.SECRET_KEY)

@asistencia_qr_bp.route("/api/asistencia/generar-qr/<int:padron>", methods=["POST"])
def generar_qr(padron):
    try:
        alumno = obtener_alumno_por_padron(padron)
        if not alumno:
            return not_found(f"Alumno con padron {padron}")
        if not alumno.get("mail"):
            return bad_request("el alumno no tiene direccion de mail registrada")

        payload = {"padron": alumno["padron"], "nombres": alumno["nombres"]}
        token = serializer.dumps(payload, salt="asistencia-qr")

        real_app = current_app._get_current_object()
        enviar_qr_async(
            real_app,
            real_app.extensions["mail"],
            alumno["mail"],
            token,
            alumno["nombres"],
            alumno["padron"])

        return { "mensaje": f"QR generado y enviandose a {alumno['mail']}" }, 202

    except Exception as e:
        return server_error(str(e))

def validar_logica_token(token):
    if not token:
        return bad_request("no se envio ningun token")
    try:
        payload = serializer.loads(token, salt="asistencia-qr", max_age=config.QR_EXPIRATION_SECONDS)
    except SignatureExpired:
        return error_response(401, "QR expirado", "error", "el codigo ha vencido")
    except BadSignature:
        return error_response(403, "QR invalido", "error", "la firma es incorrecta")

    padron = payload.get("padron")
    alumno = obtener_alumno_por_padron(padron)
    if not alumno:
        return not_found(f"alumno con padron {padron}")

    if ya_usado_token(token):
        return conflict("este codigo QR ya fue utilizado")

    if not registrar_asistencia(alumno["padron"], token):
        return server_error("no se pudo registrar la asistencia")

    fecha_hoy = date.today().isoformat()
    return {
            "mensaje": "presente registrado correctamente",
            "alumno": alumno["nombres"],
            "padron": alumno["padron"],
            "fecha": fecha_hoy
    }, 200

@asistencia_qr_bp.route("/api/asistencia/registrar", methods=["GET"])
def validar_qr():
    token = request.args.get("token")
    resultado, status_code = validar_logica_token(token)

    if status_code == 200:
        return f"""
        <html>
            <body>
                <h1>Asistencia registrada</h1>
                <p><strong>Alumno:</strong> {resultado['alumno']}</p>
                <p><strong>Padrón:</strong> {resultado['padron']}</p>
                <p><strong>Fecha:</strong> {resultado['fecha']}</p>
                <p>Gracias por confirmar tu presencia.</p>
            </body>
        </html>
        """, 200

    return resultado, status_code

"""
@asistencia_qr_bp.route("/validar-qr", methods=["POST"])
def validar_qr_post():
    data = request.get_json(silent=True)
    if not data:
        return bad_request("El cuerpo debe ser JSON")
    
    token = data.get("token")
    return validar_logica_token(token)
"""
