from flask import Blueprint, request, render_template, redirect, url_for, flash
import requests
from services.evaluaciones import crear_evaluacion, obtener_evaluaciones

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/', methods=['GET', 'POST'])
def evaluaciones():
    if request.method == 'POST':
        # Obtener datos del formulario
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
            for e in evaluacion.get('errors', ['error al crear evaluación']):
                flash(e, 'error')
        return redirect(url_for('evaluaciones.evaluaciones'))
    
    # Método GET - obtener evaluaciones existentes
    evaluaciones_lista = obtener_evaluaciones()
    return render_template('profesor-evaluaciones.html', evaluaciones=evaluaciones_lista)