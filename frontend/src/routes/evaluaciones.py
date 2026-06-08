from flask import Blueprint, app, render_template, redirect, url_for, flash, jsonify, request
import requests

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('', methods=['GET', 'POST'])
def evaluaciones():

    if requests.method == 'POST':
        # Obtener datos del formulario (sin instancia)
        datos = {
            'tipo': request.form.get('tipo'),
            'descripcion': request.form.get('descripcion'),
            'fecha': request.form.get('fecha'),
            'Curso_idCurso': request.form.get('curso_id', 1)  # Nota: Curso_idCurso
        }
        
        try:
            respuesta = requests.post(
                f"{BACK_URL}/api/evaluaciones",
                json=datos
            )
            
            if respuesta.status_code in [200, 201]:
                flash('Evaluación creada exitosamente', 'success')
            else:
                flash('Error al crear evaluación', 'error')
        except Exception as e:
            flash(f'Error de conexión: {str(e)}', 'error')
        
        return redirect(url_for('evaluaciones'))
    

    return render_template('profesor-evaluaciones.html', evaluaciones=evaluaciones)
