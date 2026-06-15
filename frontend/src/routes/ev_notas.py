from flask import Blueprint, request, render_template, url_for, redirect
from src.services import ev_notas_service as api
from src.utils import utils as utils

notas_bp = Blueprint("notas", __name__)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@notas_bp.route('/alumnos/ver', methods=['GET'])
def alumno_ver_nota():

    cursos_db = api.obtener_cursos_activos()
    tipos_db = api.obtener_evaluacion()

    padron = request.args.get('padron', type=int)
    curso_id = request.args.get('curso_id')
    id_ev = request.args.get('tipo_evaluacion')

    nota_alumno = None

    if padron and curso_id and id_ev:
        resultado = api.consultar_nota(curso_id, id_ev, padron, 'padron')

        if resultado["codigo"] == 200:
            nota_alumno = resultado["datos"]

    return render_template(
        "alumno-notas.html", 
        cursos=cursos_db, 
        tipos_evaluacion=tipos_db,
        nota = nota_alumno
    )
