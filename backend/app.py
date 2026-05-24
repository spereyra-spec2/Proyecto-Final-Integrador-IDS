from flask import Flask, Blueprint
from flask_cors import CORS
from init_db import init_db

from src.routes.ev_notas import cursos_bp

app = Flask(__name__)

CORS(app)

app.register_blueprint(cursos_bp, url_prefix='/cursos')

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)


if __name__ == "__main__":
    app.run(port=3006, debug=True)