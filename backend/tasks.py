import threading
import qrcode
import io
from flask_mail import Message

def enviar_qr_async(app, mail, email_destino, token, alumno_nombre, alumno_padron):
    def _enviar():
        with app.app_context():

            # generar qr a partir del token, guardado en memoria
            img = qrcode.make(token)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            
            # formar mensaje
            msg = Message(
                subject="Asistencia a clase - IDS",
                recipients=[email_destino]
            )
            msg.body = (
                f"Hola {alumno_nombre} (padron {alumno_padron}), \n\n"
                f"Escanea el codigo QR adjunto para confirmar tu asistencia esta clase\n"
                f"este expira en 15 minutos"
            )
            msg.attach("asistencia_qr.png", "image/png", buffer.read())
            mail.send(msg)

    # enviar al hilo, y matar el hilo si se corta el server
    hilo = threading.Thread(target=_enviar)
    hilo.daemon = True
    hilo.start()
