from xml.parsers.expat import errors
from flask import Blueprint, request, jsonify
from mysql.connector import IntegrityError
from datetime import datetime
from src.db.db import get_connection
from src.utils.errors import (
    not_found, conflict, server_error, bad_request, ok_response, well_response, acceso_denegado1, )
import src.utils.validaciones as validaciones
import src.utils.funciones as funciones

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('', methods=['POST'])
def create_evaluacion(idCurso): # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    data = request.get_json()
    

    tipo = data.get('tipo')
    descripcion = data.get('descripcion')
    fecha = data.get('fecha')

    curso_id = idCurso if idCurso else data.get('Curso_idCurso')


    if not all([tipo, descripcion, fecha, curso_id]):
        return jsonify({'error': 'Faltan campos requeridos: tipo, descripcion, fecha, curso_id'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT idCurso FROM Curso WHERE idCurso = %s", (curso_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Curso no encontrado'}), 404

        cursor.execute(
            "INSERT INTO Evaluaciones (tipo, descripcion, fecha, Curso_idCurso) VALUES (%s, %s, %s, %s)",
            (tipo, descripcion, fecha, curso_id)
        )
        conn.commit()
        
        idEvaluacion = cursor.lastrowid

        return jsonify({
            'message': 'Evaluación creada exitosamente',
            'idEvaluacion': idEvaluacion
        }), 201

    except IntegrityError as e:
        return jsonify({'error': 'Error de integridad: {}'.format(str(e))}), 400
    except Exception as e:
        return jsonify({'error': 'Error al crear la evaluación: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@evaluaciones_bp.route('', methods=['GET'])
def get_evaluaciones(idCurso):  # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Evaluaciones WHERE Curso_idCurso = %s", (idCurso,))
        evaluaciones = cursor.fetchall()

        return jsonify(evaluaciones), 200

    except Exception as e:
        return jsonify({'error': 'Error al obtener evaluaciones: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@evaluaciones_bp.route('/<int:idEvaluacion>', methods=['GET'])
def get_evaluacion(idCurso, idEvaluacion):  # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Evaluaciones WHERE idEvaluacion = %s AND Curso_idCurso = %s", (idEvaluacion, idCurso))
        evaluacion = cursor.fetchone()

        if evaluacion is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404

        return jsonify(evaluacion), 200

    except Exception as e:
        return jsonify({'error': 'Error al obtener la evaluación: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@evaluaciones_bp.route('/<int:idEvaluacion>', methods=['PUT'])
def update_evaluacion(idCurso, idEvaluacion):  # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    data = request.get_json()
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Evaluaciones WHERE idEvaluacion = %s AND Curso_idCurso = %s", (idEvaluacion, idCurso))
        evaluacion_actual = cursor.fetchone()
        
        if evaluacion_actual is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404
        
        # Usar valores actuales si no se proporcionan nuevos
        tipo = data.get('tipo', evaluacion_actual['tipo'])
        descripcion = data.get('descripcion', evaluacion_actual['descripcion'])
        fecha = data.get('fecha', evaluacion_actual['fecha'])
        curso_id = idCurso
        
        cursor.execute(
            """UPDATE Evaluaciones 
               SET tipo = %s, descripcion = %s, fecha = %s, Curso_idCurso = %s 
               WHERE idEvaluacion = %s AND Curso_idCurso = %s""",
            (tipo, descripcion, fecha, curso_id, idEvaluacion, idCurso)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM Evaluaciones WHERE idEvaluacion = %s", (idEvaluacion,))
        evaluacion_actualizada = cursor.fetchone()
        
        return jsonify({
            'message': 'Evaluación actualizada exitosamente',
            'evaluacion': evaluacion_actualizada
        }), 200

    except Exception as e:
        return jsonify({'error': 'Error al actualizar la evaluación: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()