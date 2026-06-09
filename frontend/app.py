import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.src.db.db import _get_connection 
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

CORS(app)
app.config["JSON_SORT_KEYS"] = False

app.register_blueprint(auth_bp, url_prefix="/api/auth") #sigo ejemplo del repo de cátedra
app.register_blueprint(profesor_bp, url_prefix="/api/profesor")
app.register_blueprint(alumno_bp, url_prefix="/api/alumno")
app.register_blueprint(notas_bp, url_prefix='/notas')

@app.route('/')
def index():
    return render_template('base_general.html')

@app.route('/alumno-inicio.html')
def alumno_inicio(): return render_template('alumno-inicio.html')

@app.route('/alumno-notas.html')
def alumno_notas(): return render_template('alumno-notas.html')


@app.route('/alumno-grupos.html', methods=['GET'])
def alumno_grupos():
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    

    cursor.execute("SELECT idCurso, nombre FROM Curso")
    cursos = cursor.fetchall()
    
    padron = request.args.get('padron')
    curso_id = request.args.get('curso_id')
    
    equipo_del_alumno = None
    busqueda_realizada = False
    

    if padron and curso_id:
        busqueda_realizada = True
        
        
        query_busqueda = """
            SELECT e.idEquipos, e.nombre 
            FROM Equipos e
            JOIN Usuarios_has_Equipos uhe ON e.idEquipos = uhe.Equipos_idEquipos
            WHERE uhe.Usuarios_padron = %s AND e.Curso_idCurso = %s AND uhe.activo = 1
        """
        cursor.execute(query_busqueda, (padron, curso_id))
        equipo_del_alumno = cursor.fetchone()
        
    cursor.close()
    conn.close()
    
    return render_template(
        'alumno-grupos.html', 
        cursos=cursos,
        padron=padron,
        curso_id=int(curso_id) if curso_id else None,
        equipo_del_alumno=equipo_del_alumno,
        busqueda_realizada=busqueda_realizada
    )

@app.route('/alumno-asistencia.html')
def alumno_asistencia(): return render_template('alumno-asistencia.html')

@app.route('/login.html')
def login(): return render_template('login.html')

@app.route('/profesor-equipos.html')
def profe_equipos(): return render_template('profesor-equipos.html')

@app.route('/profesor-dashboard.html')
def docente_dashboard(): return render_template('profesor-dashboard.html')

@app.route('/profesor-evaluaciones.html')
def docente_evaluaciones(): return render_template('profesor-evaluaciones.html')

@app.route('/profesor-cursos.html')
def docente_cursos(): return render_template('profesor-cursos.html')

@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static', 'css'), filename)

@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static', 'js'), filename)

if __name__ == "__main__":
    app.run(port=5000, debug=True)