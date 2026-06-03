import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from backend.init_db import init_db
from backend.src.routes.equipos import equipos_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
    static_folder=os.path.join(BASE_DIR, 'frontend', 'static')
)

CORS(app)
app.config["JSON_SORT_KEYS"] = False

app.register_blueprint(equipos_bp)

try:
    init_db()
except Exception as e:
    print(f"Error al inicializar la base de datos: {e}")
    exit(1)

@app.route('/')
def index():
    return render_template('base_general.html')


@app.route('/alumno-inicio.html')
def alumno_inicio():
    return render_template('alumno-inicio.html')

@app.route('/alumno-notas.html')
def alumno_notas():
    return render_template('alumno-notas.html')

@app.route('/alumno-grupos.html')
def alumno_grupos():
    return render_template('alumno-grupos.html')

@app.route('/alumno-asistencia.html')
def alumno_asistencia():
    return render_template('alumno-asistencia.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/profesor-equipos.html')
def profe_equipos():
    return render_template('profesor-equipos.html')

@app.route('/profesor-dashboard.html')
def docente_dashboard():
    return render_template('profesor-dashboard.html')

@app.route('/profesor-evaluaciones.html')
def docente_evaluaciones():
    return render_template('profesor-evaluaciones.html')

@app.route('/profesor-cursos.html')
def docente_cursos():
    return render_template('profesor-cursos.html')

@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory("templates/css", filename)

@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory("templates/js", filename)

if __name__ == "__main__":
    app.run(port=5000, debug=True)