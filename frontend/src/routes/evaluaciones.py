from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from src.services.evaluaciones import obtener_evaluaciones, crear_evaluacion, actualizar_evaluacion
from src.utils import utils
from src.routes.profesor import profesor_bp

@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones', methods=['GET', 'POST'])
def evaluaciones(curso_id):
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder al panel.", "error")
        return redirect(url_for('auth.login'))
    
    token = usuario.get('token')

    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form.get('fecha', '').strip()
        
        errores = []

        if not tipo or not descripcion or not fecha:
            errores.append("Todos los campos son obligatorios.")

        if errores:
            for e in errores:
                flash(e, 'error')
            return redirect(url_for('evaluaciones.evaluaciones', curso_id=curso_id))
        
        resultado = crear_evaluacion(token, tipo, descripcion, fecha, int(curso_id))
        
        if resultado.get('ok'):
            flash(resultado.get('message', 'Evaluación creada exitosamente'), 'success')
        else:
            errores_lista = resultado.get('error_response', {}).get('errors', [])
            for e in errores_lista:
                flash(e.get('description', 'Error al crear evaluación'), 'error')
        
        return redirect(url_for('evaluaciones.evaluaciones', curso_id=curso_id))
    
    # GET: obtener evaluaciones - PASAR EL TOKEN
    resultado = obtener_evaluaciones(token, curso_id=int(curso_id))
    
    evaluaciones_lista = []
    if resultado.get('ok'):
        evaluaciones_lista = resultado.get('evaluaciones', [])
    else:
        errores_lista = resultado.get('error_response', {}).get('errors', [])
        for e in errores_lista:
            flash(e.get('description', 'Error al obtener evaluaciones'), 'error')
    
    return render_template('profesor-evaluaciones.html', evaluaciones=evaluaciones_lista)


@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones/<int:id>', methods=['GET'])
def api_get_evaluacion(id):
    """API para obtener una evaluación específica (para editar)"""
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return jsonify({'error': 'No autorizado'}), 401
    
    token = usuario.get('token')
    resultado = obtener_evaluaciones(token, id)
    
    if resultado.get('ok'):
        evaluaciones = resultado.get('evaluaciones', [])
        # Si es una lista, tomamos el primer elemento
        if isinstance(evaluaciones, list) and len(evaluaciones) > 0:
            evaluacion = evaluaciones[0]
        elif isinstance(evaluaciones, dict):
            evaluacion = evaluaciones
        else:
            evaluacion = None
        
        if evaluacion:
            return jsonify(evaluacion)
    
    return jsonify({'error': 'Evaluación no encontrada'}), 404


@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones/actualizar/<int:idEvaluacion>', methods=['POST'])
def actualizar_evaluacion_route(curso_id,idEvaluacion):
    """Actualiza una evaluación usando formulario POST"""
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder al panel.", "error")
        return redirect(url_for('auth.login'))
    
    token = usuario.get('token')
    
    # Obtener valores del formulario (solo los que vienen)
    tipo = request.form.get('tipo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    fecha = request.form.get('fecha', '').strip()
    
    # Solo pasar los campos que tienen valor
    resultado = actualizar_evaluacion(
        token, 
        idEvaluacion,
        tipo=tipo if tipo else None,
        descripcion=descripcion if descripcion else None,
        fecha=fecha if fecha else None,
        curso_id=int(curso_id)
    )
    
    if resultado.get('ok'):
        flash('✅ Evaluación actualizada exitosamente', 'success')
    else:
        errores_lista = resultado.get('error_response', {}).get('errors', [])
        for e in errores_lista:
            flash(f'❌ Error: {e.get("description", "Error al actualizar")}', 'error')
    
    return redirect(url_for('evaluaciones.evaluaciones', curso_id=curso_id))