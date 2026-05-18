from flask import Blueprint, request, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature, serializer
from db import obtener_alumno_por_padron, ya_usado_token, registrar_asistencia
from tasks import enviar_qr_async
from src.utils.errors import error_response, bad_request, not_found, server_error, conflict
import config
from datetime import date

asistencia_qr_bp = Blueprint("asistencia_qr", __name__)
serializer = URLSafeTimedSerializer(config.SECRET_KEY)

@asistencia_qr_bp.route("/generar-qr/<int:padron>", methods=["POST"])
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

@asistencia_qr_bp.route("/validar_qr", methods=["POST"])
def validar_qr():
    try:
        data = request.get_json(silent=True)
        if not data or "token" not in data:
            return bad_request("el cuerpo debe incluir el campo 'token'")

        token = data["token"]

        try:
            payload = serializer.loads(token, salt="asistencia-qr", max_age=config.QR_EXPIRATION_SECONDS)
        except SignatureExpired:
            return error_response(401, "QR expirado", "warning", "el codigo ha vencido")
        except BadSignature:
            return error_response(403, "QR invalido", "error", "la firma criptografica es incorrecta")

        padron = payload.get("padron")
        alumno = obtener_alumno_por_padron(padron)
        if not alumno:
            return not_found(f"alumno con padron {padron}")

        if ya_usado_token(token):
            return conflict("este codigo QR ya fue utilizado")

        if not registrar_asistencia(alumno["padron"], token):
            return server_error("no se pudo registrar la asistencia en la base de datos")

        fecha_hoy = date.today().isoformat()
        return {
            "mensaje": "presente registrado correctamente",
            "alumno": alumno["nombres"],
            "padron": alumno["padron"],
            "fecha": fecha_hoy
        }, 200

    except Exception as e:
        return server_error(str(e))
