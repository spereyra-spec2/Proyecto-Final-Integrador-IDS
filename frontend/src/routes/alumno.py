from flask import Blueprint, render_template, request
from src.services import cursos as api_cursos
from src.services import ev_notas_service as api_notas

alumno_bp = Blueprint('alumno', __name__)

@alumno_bp.route('/inicio', methods=['GET'])
def inicio():
    resultado = api_cursos.obtener_cursos(token=None) 
    
    cursos_todos = []
    if resultado.get('ok'):
        cursos_todos = resultado.get('cursos', [])
        
    cursos_activos = [c for c in cursos_todos if c.get('estado') == 'activo' or c.get('Estado') == 1]
    
    return render_template('alumno-inicio.html', cursos=cursos_activos)

@alumno_bp.route('/notas/ver', methods=['GET'])
def alumno_ver_nota():

    cursos_db = api_notas.obtener_cursos_activos()
    
    #Guardo el curso elegido por el alumno
    curso_id = request.args.get('curso_id')
    padron = request.args.get('padron', type=int)
    id_ev = request.args.get('tipo_evaluacion')

    tipos_db = api_notas.obtener_evaluacion(curso_id=curso_id)

    nota_alumno = None
    error_msg = None

    if padron and curso_id and id_ev:
        resultado = api_notas.consultar_nota(curso_id, id_ev, padron, 'padron')
        if resultado["codigo"] == 200:
            nota_alumno = resultado["datos"]
        else:
            error_msg = resultado["error"]

    return render_template('alumno-notas.html', 
                           cursos_db=cursos_db, 
                           tipos_db=tipos_db, 
                           curso_id=curso_id, 
                           padron=padron, 
                           id_ev=id_ev, 
                           nota_alumno=nota_alumno,
                           error=error_msg)
