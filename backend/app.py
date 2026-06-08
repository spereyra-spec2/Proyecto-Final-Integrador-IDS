import os
from flask import Flask
from flask_cors import CORS
from init_db import init_db
from src.routes.equipos import equipos_bp 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
CORS(app)

app.config["JSON_SORT_KEYS"] = False

app.register_blueprint(equipos_bp, url_prefix="/api/cursos")

try:
    init_db()
except Exception as e:
    print(f"Error al inicializar la base de datos: {e}")
    exit(1)

if __name__ == "__main__":
    app.run(port=5001, debug=True) 