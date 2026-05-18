from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from src.routes.asistencia_por_qr import asistencia_qr_bp
import config

def configure_app(app):
    # Carga toda la configuración desde el módulo config.py. 
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAIL_SERVER"] = config.MAIL_SERVER
    app.config["MAIL_PORT"] = config.MAIL_PORT
    app.config["MAIL_USE_TLS"] = config.MAIL_USE_TLS
    app.config["MAIL_USERNAME"] = config.MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = config.MAIL_PASSWORD
    app.config["MAIL_DEFAULT_SENDER"] = config.MAIL_USERNAME

def init_mail(app):
    # Inicializa la extensión Mail y la guarda en app.extensions.
    mail = Mail(app)
    app.extensions["mail"] = mail
    return mail

def create_app():
    app = Flask(__name__)

    configure_app(app)
    init_mail(app)

    CORS(app)
    app.register_blueprint(asistencia_qr_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
