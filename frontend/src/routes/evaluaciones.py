from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from backend.src.db.db import get_connection
from src.services.evaluaciones import actualizar_evaluacion, actualizar_evaluacion, crear_evaluacion, obtener_evaluaciones

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/', methods=['GET', 'POST'])
def evaluaciones():
    if request.method == 'POST':

        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form.get('fecha', '').strip()
        curso_id = request.form.get('curso_id', '').strip()
        
        errores = []

        if not tipo or not descripcion or not fecha or not curso_id:
            errores.append("Todos los campos son obligatorios.")

        if errores:
            for e in errores:
                flash(e, 'error')
            return redirect(url_for('evaluaciones.evaluaciones'))
        
        
        evaluacion = crear_evaluacion(tipo, descripcion, fecha, int(curso_id))
        
        if evaluacion.get('ok'):
            flash(evaluacion.get('message', 'Evaluación creada exitosamente'), 'success')
        else:
            for e in evaluacion.get('errors', ['Error al crear evaluación']):
                flash(e, 'error')
        
        return redirect(url_for('evaluaciones.evaluaciones'))
    
    evaluaciones_lista = obtener_evaluaciones()

    if evaluaciones_lista is None:
        evaluaciones_lista = []
    
    return render_template('profesor-evaluaciones.html', evaluaciones=evaluaciones_lista)

@evaluaciones_bp.route('api/evaluaciones/<int:id>', methods=['GET'])
def api_get_evaluacion(id):
    """API para obtener una evaluación específica (para editar)"""
    evaluacion = obtener_evaluaciones(id)
    if evaluacion:
        return jsonify(evaluacion)
    return jsonify({'error': 'Evaluación no encontrada'}), 404


@evaluaciones_bp.route('/actualizar/<int:idEvaluacion>', methods=['POST'])
def actualizar_evaluacion_route(idEvaluacion):
    """Actualiza una evaluación usando formulario POST"""
    
    # Obtener la evaluación actual para mantener valores no enviados
    evaluacion_actual = obtener_evaluaciones(idEvaluacion)
    
    if not evaluacion_actual:
        flash('Evaluación no encontrada', 'error')
        return redirect(url_for('evaluaciones.evaluaciones'))
    
    # Obtener valores del formulario (solo los que vienen)
    tipo = request.form.get('tipo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    fecha = request.form.get('fecha', '').strip()
    curso_id = request.form.get('curso_id', '').strip()
    
    # Usar valores actuales si los campos están vacíos
    if not tipo:
        tipo = evaluacion_actual.get('tipo')
    if not descripcion:
        descripcion = evaluacion_actual.get('descripcion', '')
    if not fecha:
        fecha = evaluacion_actual.get('fecha')
    if not curso_id:
        curso_id = evaluacion_actual.get('Curso_idCurso')
    else:
        curso_id = int(curso_id)
    
    # Llamar al servicio de actualización
    resultado = actualizar_evaluacion(idEvaluacion, tipo, descripcion, fecha, curso_id)
    
    if resultado.get('ok'):
        flash('✅ Evaluación actualizada exitosamente', 'success')
    else:
        flash(f'❌ Error: {resultado.get("message", "Error al actualizar")}', 'error')
    
    return redirect(url_for('evaluaciones.evaluaciones'))