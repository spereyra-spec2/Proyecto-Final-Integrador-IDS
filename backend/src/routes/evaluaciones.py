from flask import Blueprint, request, jsonify
from mysql.connector import IntegrityError
from datetime import datetime
from db import get_connection

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/evaluaciones', methods=['POST'])
def create_evaluacion():
    data = request.get_json()
    curso_id = data.get('curso_id')
    notas_id = data.get('notas_id')

    if not all([curso_id, notas_id]):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar que el curso exista
        cursor.execute("SELECT id FROM cursos WHERE id = %s", (curso_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Curso no encontrado'}), 404
        

        # Insertar la evaluación
        fecha_evaluacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO evaluaciones (tipo,descripcion,fecha,curso_id, notas_id) VALUES (%s, %s, %s, %s, %s)",
            ( tipo, descripcion, fecha, curso_id, notas_id)
        )
        conn.commit()

        return jsonify({'message': 'Evaluación creada exitosamente'}), 201

    except IntegrityError as e:
        return jsonify({'error': 'Error de integridad: {}'.format(str(e))}), 400
    except Exception as e:
        return jsonify({'error': 'Error al crear la evaluación: {}'.format(str(e))}), 500
    finally:
        cursor.close()
        conn.close()

@evaluaciones_bp.route('/evaluaciones/<int:evaluacion_id>', methods=['GET'])
def get_evaluacion(evaluacion_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM evaluaciones WHERE evaluacion_ID = %s", (evaluacion_id,))
        evaluacion = cursor.fetchone()

        if evaluacion is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404

        return jsonify(evaluacion), 200

    except Exception as e:
        return jsonify({'error': 'Error al obtener la evaluación: {}'.format(str(e))}), 500
    finally:
        cursor.close()
        conn.close()

@evaluaciones_bp.route('/evaluaciones/<int:evaluacion_id>', methods=['PATCH'])
def update_evaluacion(evaluacion_id):
    data = request.get_json()
    tipo = data.get('tipo')
    descripcion = data.get('descripcion')
    fecha = data.get('fecha')

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar que la evaluación exista
        cursor.execute("SELECT evaluacion_ID FROM evaluaciones WHERE evaluacion_ID = %s", (evaluacion_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404

        # Actualizar la evaluación
        cursor.execute(
            "UPDATE evaluaciones SET tipo = %s, descripcion = %s, fecha = %s WHERE evaluacion_ID = %s",
            (tipo, descripcion, fecha, evaluacion_id)
        )
        conn.commit()

        return jsonify({'message': 'Evaluación actualizada exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': 'Error al actualizar la evaluación: {}'.format(str(e))}), 500
    finally:
        cursor.close()
        conn.close()