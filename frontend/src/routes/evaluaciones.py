# GESTIÓN DE EVALUACIONES
#---------------------------------------------------------------------------------------------------------

from flask import Blueprint, jsonify, render_template, request, flash, redirect, session, url_for
from src.utils import utils
from src.services.evaluaciones import obtener_evaluaciones, crear_evaluacion, actualizar_evaluacion, eliminar_evaluacion
from src.services import cursos as cursos_service  # ← Cambiar el alias para evitar conflicto


# Blueprint de nivel 3 (más interno)
evaluaciones_bp = Blueprint('evaluaciones', __name__, url_prefix='/<int:idCurso>/evaluaciones')


@evaluaciones_bp.route('', methods=['GET', 'POST'])
def evaluaciones(curso_id):
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder al panel.", "error")
        return redirect(url_for('auth.login'))
    
    token = usuario.get('token')
    session['curso_actual'] = curso_id

    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form.get('fecha', '').strip()
        
        if not tipo or not descripcion or not fecha:
            flash("Todos los campos son obligatorios", "error")
            return redirect(url_for('profesor.cursos.evaluaciones.evaluaciones', curso_id=curso_id))
        
        resultado = crear_evaluacion(token, tipo, descripcion, fecha, curso_id)  # ← Usar función directa
        
        if resultado.get('ok'):
            flash(resultado.get('message', 'Evaluación creada exitosamente'), 'success')
        else:
            errores = resultado.get('error_response', {}).get('errors', [])
            for e in errores:
                flash(e.get('description', 'Error al crear evaluación'), 'error')
        
        return redirect(url_for('profesor.cursos.evaluaciones.evaluaciones', curso_id=curso_id))
    
    # GET: obtener evaluaciones
    resultado = obtener_evaluaciones(token, curso_id=curso_id)  # ← Usar función directa
    
    evaluaciones_lista = []
    if resultado.get('ok'):
        evaluaciones_lista = resultado.get('evaluaciones', [])
    else:
        errores = resultado.get('error_response', {}).get('errors', [])
        for e in errores:
            flash(e.get('description', 'Error al obtener evaluaciones'), 'error')
    
    # Obtener información del curso actual
    cursos_resultado = cursos_service.obtener_cursos_del_profesor(token)  # ← Usar el módulo con alias
    cursos = cursos_resultado.get('cursos', []) if cursos_resultado.get('ok') else []
    curso_actual = next((c for c in cursos if c.get('idCurso') == curso_id), {'idCurso': curso_id, 'nombre': f'Curso {curso_id}'})
    
    return render_template('profesor-evaluaciones.html', 
                         evaluaciones=evaluaciones_lista,
                         cursos=cursos,
                         curso=curso_actual, 
                         curso_id=curso_id)

#-----------------------------------------------------------------------------------------------------
@evaluaciones_bp.route('/<int:id>', methods=['GET'])
def api_get_evaluacion(curso_id, id): 
    """API para obtener una evaluación específica (para editar)"""
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return jsonify({'error': 'No autorizado'}), 401
    
    token = usuario.get('token')
    resultado = obtener_evaluaciones(token, curso_id, id)  # ← Pasar curso_id también
    
    if resultado.get('ok'):
        evaluaciones = resultado.get('evaluaciones', [])
        if isinstance(evaluaciones, list) and len(evaluaciones) > 0:
            evaluacion = evaluaciones[0]
        elif isinstance(evaluaciones, dict):
            evaluacion = evaluaciones
        else:
            evaluacion = None
        
        if evaluacion:
            return jsonify(evaluacion)
    
    return jsonify({'error': 'Evaluación no encontrada'}), 404

#----------------------------------------------------------------------------------------------------
@evaluaciones_bp.route('/actualizar/<int:idEvaluacion>', methods=['POST'])
def actualizar_evaluacion_route(curso_id, idEvaluacion):
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder al panel.", "error")
        return redirect(url_for('auth.login'))
    
    token = usuario.get('token')
    
    tipo = request.form.get('tipo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    fecha = request.form.get('fecha', '').strip()
    
    resultado = actualizar_evaluacion(  # ← Usar función directa
        token, 
        idEvaluacion,
        tipo=tipo if tipo else None,
        descripcion=descripcion if descripcion else None,
        fecha=fecha if fecha else None,
        curso_id=curso_id
    )
    
    if resultado.get('ok'):
        flash('✅ Evaluación actualizada exitosamente', 'success')
    else:
        errores_lista = resultado.get('error_response', {}).get('errors', [])
        for e in errores_lista:
            flash(f'❌ Error: {e.get("description", "Error al actualizar")}', 'error')
    
    return redirect(url_for('profesor.cursos.evaluaciones.evaluaciones', curso_id=curso_id))