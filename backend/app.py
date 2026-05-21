from flask import Flask
from flask_cors import CORS
from init_db import init_db
from src.routes.alumnos import alumnos_bp

from config import URL_BASE

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

app.register_blueprint(alumnos_bp, url_prefix=f'/{URL_BASE}/cursos/<curso_id>/alumnos')

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)


if __name__ == "__main__":
    app.run(port=3006, debug=True)
