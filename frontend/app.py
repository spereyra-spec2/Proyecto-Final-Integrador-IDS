import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.src.db.db import get_connection 
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_cors import CORS
from src.routes.auth import auth_bp
from src.routes.profesor import profesor_bp
from src.routes.alumno import alumno_bp
from src.routes.ev_notas import notas_bp

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

app.json.sort_keys = False
app.secret_key = 'supersecretkey'

CORS(app)
app.config["JSON_SORT_KEYS"] = False
app.config['SECRET_KEY'] = 'clave_secreta_ids_2026'

app.register_blueprint(auth_bp, url_prefix="/auth") #sigo ejemplo del repo de cátedra
app.register_blueprint(profesor_bp, url_prefix="/profesor")
app.register_blueprint(alumno_bp, url_prefix="/alumno")
app.register_blueprint(notas_bp, url_prefix='/notas')
app.register_blueprint(asistencias_bp, url_prefix='/asistencia')



@app.route('/')
def index():
    return render_template('base_general.html')

@app.route('/alumno-inicio.html')
def alumno_inicio():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT idCurso AS id, nombre, codigo FROM Curso")
    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('alumno-inicio.html', cursos=cursos)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
