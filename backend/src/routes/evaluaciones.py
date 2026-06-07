from flask import Blueprint, request, jsonify
from mysql.connector import IntegrityError
from datetime import datetime
from src.db.db import get_connection

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('', methods=['POST'])
def create_evaluacion():
    data = request.get_json()
    
    # Obtener todos los campos
    tipo = data.get('tipo')
    descripcion = data.get('descripcion')
    fecha = data.get('fecha')
    curso_id = data.get('curso_id')

    # Validar campos requeridos
    if not all([tipo, descripcion, fecha, curso_id]):
        return jsonify({'error': 'Faltan campos requeridos: tipo, descripcion, fecha, curso_id'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar que el curso exista (usando curso_id como está en tu tabla)
        cursor.execute("SELECT curso_id FROM Curso WHERE curso_id = %s", (curso_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Curso no encontrado'}), 404

        # Insertar la evaluación (usando los campos correctos)
        cursor.execute(
            "INSERT INTO Evaluaciones (tipo, descripcion, fecha, curso_id) VALUES (%s, %s, %s, %s)",
            (tipo, descripcion, fecha, curso_id)
        )
        conn.commit()
        
        evaluacion_id = cursor.lastrowid

        return jsonify({
            'message': 'Evaluación creada exitosamente',
            'evaluacion_id': evaluacion_id
        }), 201

    except IntegrityError as e:
        return jsonify({'error': 'Error de integridad: {}'.format(str(e))}), 400
    except Exception as e:
        return jsonify({'error': 'Error al crear la evaluación: {}'.format(str(e))}), 500
    finally:
        cursor.close()
        conn.close()


@evaluaciones_bp.route('', methods=['GET'])
def get_evaluaciones():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Evaluaciones")
        evaluaciones = cursor.fetchall()

        return jsonify(evaluaciones), 200

    except Exception as e:
        return jsonify({'error': 'Error al obtener evaluaciones: {}'.format(str(e))}), 500
    finally:
        cursor.close()
        conn.close()


@evaluaciones_bp.route('/<int:evaluacion_id>', methods=['GET'])
def get_evaluacion(evaluacion_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Evaluaciones WHERE evaluacion_ID = %s", (evaluacion_id,))
        evaluacion = cursor.fetchone()

        if evaluacion is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404

        return jsonify(evaluacion), 200

    except Exception as e:
        return jsonify({'error': 'Error al obtener la evaluación: {}'.format(str(e))}), 500
    finally:
        cursor.close()
        conn.close()


@evaluaciones_bp.route('/<int:evaluacion_id>', methods=['PUT'])
def update_evaluacion(evaluacion_id):
    data = request.get_json()
    tipo = data.get('tipo')
    descripcion = data.get('descripcion')
    fecha = data.get('fecha')
    curso_id = data.get('curso_id')

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar que la evaluación exista
        cursor.execute("SELECT evaluacion_ID FROM Evaluaciones WHERE evaluacion_ID = %s", (evaluacion_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404

        # Actualizar la evaluación
        cursor.execute(
            "UPDATE Evaluaciones SET tipo = %s, descripcion = %s, fecha = %s, curso_id = %s WHERE evaluacion_ID = %s",
            (tipo, descripcion, fecha, curso_id, evaluacion_id)
        )
        conn.commit()

        return jsonify({'message': 'Evaluación actualizada exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': 'Error al actualizar la evaluación: {}'.format(str(e))}), 500
    finally:
        cursor.close()
        conn.close()
