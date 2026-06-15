from flask import Blueprint, render_template
from src.services import cursos as api_cursos

alumno_bp = Blueprint('alumno', __name__)

@alumno_bp.route('/inicio', methods=['GET'])
def inicio():
    resultado = api_cursos.obtener_cursos(token=None) 
    
    cursos_todos = []
    if resultado.get('ok'):
        cursos_todos = resultado.get('cursos', [])
        
    cursos_activos = [c for c in cursos_todos if c.get('estado') == 'activo' or c.get('Estado') == 1]
    
    return render_template('alumno-inicio.html', cursos=cursos_activos)