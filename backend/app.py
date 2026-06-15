import os
from flask import Flask
from flask_cors import CORS
from src.routes.auth.auth import auth_bp
from src.routes.api_ev_notas import ev_notas_bp
from src.routes.equipos import equipos_bp
from src.routes.alumnos import alumnos_bp
from src.routes.cursos import cursos_bp
from src.routes.evaluaciones import evaluaciones_bp
from src.routes.asistencia import asistencia_bp
from src.db.init_db import init_db

from mail import mail

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
CORS(app)

app.config["JSON_SORT_KEYS"] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'gestion.academica.ids@gmail.com'
app.config['MAIL_PASSWORD'] = 'xdkv alji fnmx euxz'


app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(ev_notas_bp, url_prefix="/api/notas")
app.register_blueprint(alumnos_bp, url_prefix='/api/cursos/<int:idCurso>/alumnos')
app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
app.register_blueprint(equipos_bp, url_prefix='/api/cursos')
app.register_blueprint(evaluaciones_bp, url_prefix='/api/cursos/<int:idCurso>/evaluaciones')
app.register_blueprint(asistencia_bp, url_prefix='/api/asistencia')

mail.init_app(app)

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
