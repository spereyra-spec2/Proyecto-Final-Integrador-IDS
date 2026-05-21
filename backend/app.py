from flask import Flask
from flask_cors import CORS
from init_db import init_db
from src.routes.asistencia import asistencia_bp
import config

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = config.SECRET_KEY

app.register_blueprint(asistencia_bp, url_prefix="/api/asistencia")

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
