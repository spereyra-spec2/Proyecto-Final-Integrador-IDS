from flask import Blueprint, request, render_template, url_for, redirect


from frontend.src.services import ev_notas_service as api

notas_bp = Blueprint("notas", __name__)

@notas_bp.route('/ver', methods=['GET'])
def vista_ver_nota():
    curso_id = request.args.get('curso_id')
    id_ev = request.args.get('id_ev')
    tipo = request.args.get('tipo')
    id_g = request.args.get('id_g')


    if not curso_id and not id_ev and not id_g and not tipo:
        return render_template('ver_nota.html', nota=None, error=None)

    resultado = api.consultar_nota(curso_id, id_ev, id_g, tipo)

    if resultado["codigo"] == 200:
        return render_template('ver_nota.html', nota=resultado["datos"], error=None,curso_id=curso_id, id_evaluaciones=id_ev, identificador=id_g)
    else:
        return render_template('ver_nota.html', nota=None, error=resultado["error"], curso_id=curso_id, id_evaluaciones=id_ev, identificador=id_g)


@notas_bp.route('/cargar', methods=['GET', 'POST'])
def procesar_guardado():

    if request.method == 'POST':

        curso_id = request.form.get('curso_id')
        id_evaluacion = request.form.get('id_evaluacion')
        id_g = request.form.get('id_g')
        nota = request.form.get('nota')
        tipo = request.args.get('tipo')

        resultado = api.cargar_nota(curso_id, id_evaluacion, id_g, nota, tipo)

        if resultado["codigo"] == 201:
            # Determino un nuevo valor para 'estado'.
            return redirect(url_for('notas.procesar_guardado', estado='ok'))
        else:
            return f"<h3>Se ha producido un error al cargar la nota: {resultado['error']}</h3><a href='/notas/cargar'>Volver a intentar</a>", resultado["codigo"]

    estado = request.args.get('estado')
    return render_template('cargar_nota.html', estado=estado)


@notas_bp.route('/editar', methods=['GET', 'POST'])
def procesar_actualizacion():

    if request.method == 'POST':

        curso_id = request.form.get('curso_id')
        id_evaluacion = request.form.get('id_evaluacion')
        identificador = request.form.get('id_g')    
        nota_nueva = request.form.get('nota')
        tipo = request.args.get('tipo')

        resultado = api.actualizar_nota(curso_id, id_evaluacion, identificador, nota_nueva, tipo)

        if resultado["codigo"] == 200:
            return redirect(f"/notas/ver?curso_id={curso_id}&id_ev={id_evaluacion}&identificador={identificador}")
        
        else:
            return f"<h3>Error al actualizar: {resultado['error']}</h3><a href='javascript:history.back()'>Regresar</a>", resultado["codigo"]
    
    contexto = {'curso_id': request.args.get('curso_id'), 'id_ev': request.args.get('id_ev'), 'padron': request.args.get('padron'), 'tipo': request.args.get('tipo')}
    return render_template('editar_nota.html', **contexto)