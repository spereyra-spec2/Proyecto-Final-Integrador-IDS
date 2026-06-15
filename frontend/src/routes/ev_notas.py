from flask import Blueprint, request, render_template, url_for, redirect
from src.services import ev_notas_service as api
from src.utils import utils as utils

notas_bp = Blueprint("notas", __name__)



@notas_bp.route('/ver', methods=['GET'])
def ver_nota():

    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))

    curso_id = request.args.get('curso_id')
    id_ev = request.args.get('id_ev')
    tipo = request.args.get('tipo')
    id_g = request.args.get('id_g')


    if not curso_id and not id_ev and not id_g and not tipo:
        return render_template('ver_nota.html', nota=None, error=None)

    resultado = api.consultar_nota(curso_id, id_ev, id_g, tipo)

    if resultado["codigo"] == 200:
        return render_template('ver_nota.html', nota=resultado["datos"], error=None,curso_id=curso_id, id_evaluaciones=id_ev, id_g=id_g, tipo=tipo)
    else:
        return render_template('ver_nota.html', nota=None, error=resultado["error"], curso_id=curso_id, id_evaluaciones=id_ev, id_g=id_g, tipo=tipo)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------

@notas_bp.route('/cargar', methods=['GET', 'POST'])
def procesar_guardado():

    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))

    if request.method == 'POST':

        curso_id = request.form.get('curso_id')
        id_evaluacion = request.form.get('id_evaluacion')
        id_g = request.form.get('id_g')
        nota = request.form.get('nota')
        tipo = request.form.get('tipo')

        resultado = api.cargar_nota(curso_id, id_evaluacion, id_g, nota, tipo)

        if resultado["codigo"] in [200, 201]:
            # Determino un nuevo valor para 'estado'.
            return redirect(url_for('notas.procesar_guardado', estado='ok'))
        else:
            return render_template('manejo_de_error.html', error_msg=resultado['error']), resultado["codigo"]

    estado = request.args.get('estado')
    return render_template('cargar_nota.html', estado=estado)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@notas_bp.route('/editar', methods=['GET', 'POST'])
def procesar_actualizacion():

    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))

    if request.method == 'POST': 

        curso_id = request.form.get('curso_id')
        id_ev = request.form.get('id_ev')
        id_g = request.form.get('id_g')    
        nota_nueva = request.form.get('nota')
        tipo = request.form.get('tipo')

        resultado = api.actualizar_nota(curso_id, id_ev, id_g, nota_nueva, tipo)

        if resultado["codigo"] == 200:
            return redirect(f"/notas/ver?curso_id={curso_id}&id_ev={id_ev}&id_g={id_g}&tipo={tipo}")
        else:
            return render_template('manejo_de_error.html', error_msg=resultado['error']), resultado["codigo"]
    
    query_params = {
        'curso_id': request.args.get('curso_id'), 
        'id_ev': request.args.get('id_ev'), 
        'id_g': request.args.get('id_g'), 
        'tipo': request.args.get('tipo')
    }
    return render_template('editar_nota.html', **query_params)

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
