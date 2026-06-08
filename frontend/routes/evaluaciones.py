from flask import Blueprint, app, render_template, redirect, url_for, flash, jsonify, request
import requests

from frontend.services.evaluaciones import crear_evaluacion



evaluaciones_bp = Blueprint('evaluaciones', __name__)



@evaluaciones_bp.route('', methods=['GET', 'POST'])
def evaluaciones():

    if requests.method == 'POST':
        # Obtener datos del formulario (sin instancia)
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
        
            return redirect(url_for('evaluaciones'))
        evaluacion = crear_evaluacion(tipo, descripcion, fecha, int(curso_id))
        if evaluacion.get('ok'):
            flash(evaluacion.get('message', 'Evaluación creada exitosamente'), 'success')
        else:
            for e in evaluacion.get('errors', ['error al crear evaluación']):
                flash(e, 'error')
        return redirect(url_for('evaluaciones'))
            
    return render_template('profesor-evaluaciones.html', evaluaciones=evaluaciones)
