from flask import Flask
from init_db import init_db
from flask_cors import CORS
from src.routes.asistencia_por_qr import asistencia_qr_bp
import config

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = config.SECRET_KEY

    CORS(app)
    app.register_blueprint(asistencia_qr_bp, url_prefix="/api")

    return app

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
