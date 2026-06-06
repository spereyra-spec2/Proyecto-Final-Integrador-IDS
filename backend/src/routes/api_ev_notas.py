from flask import Blueprint, request, jsonify
import mysql.connector
from db import get_connection
    
from src.db.ev_notas_db import validar_id, validar_curso, validar_evaluacion, validar_equipo
from src.utils.validar_numeros import valido_numero
from src.utils.errors_ev_notas import error_400, error_404, error_500


api_bp=Blueprint('api', __name__)


@api_bp.route('/curso/<curso_id>/evaluaciones/<id_evaluacion>/notas', methods=['GET'])
def obtener_nota(curso_id, id_evaluacion):

    padron = request.args.get('padron', type=int)
    id_equipo = request.args.get('id_equipo', type=int)


    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:

        if not valido_numero(id_evaluacion):
            return jsonify(error_400("El id de la evaluación debe ser un número entero positivo.")), 400
        
        if not valido_numero(curso_id):
            return jsonify(error_400("El id del curso debe ser un número entero positivo.")), 400

        if validar_curso(curso_id) == None:
            return jsonify(error_404(f"No se encontró el curso con id {curso_id}.")), 404
            
        if validar_evaluacion(id_evaluacion) == None:
            return jsonify(error_404(f"No se encontró la evaluación con id {id_evaluacion}.")), 404
        
        nota = None
        
        if id_equipo:
            
            if not valido_numero(id_equipo):
                return jsonify(error_400("El id del equipo debe ser un numero entero positivo.")), 400
            
            if validar_equipo(id_equipo) == None:
                return jsonify(error_404(f"No se encontró el equipo con id {id_equipo}.")), 404

            query_g = """
                SELECT n.puntaje, e.tipo
                FROM Notas n
                INNER JOIN Evaluaciones e ON n.Evaluaciones_idEvaluacion = e.idEvaluacion
                WHERE e.Curso_idCurso = %s AND n.Equipos_idEquipos = %s AND e.idEvaluacion = %s
            """
            cursor.execute(query_g, (curso_id, id_equipo, id_evaluacion))
            nota = cursor.fetchone()
        
        elif padron:

            if not valido_numero(padron):
                return jsonify(error_400("El padrón debe ser un número entero positivo.")), 400

            if validar_id(padron) == None:
                return jsonify(error_404(f"No se encontró al alumno con padrón {padron}.")), 404

            query = """
                SELECT n.puntaje, e.tipo
                FROM Notas n
                INNER JOIN Evaluaciones e ON n.Evaluaciones_idEvaluacion = e.idEvaluacion
                WHERE e.Curso_idCurso = %s AND n.Usuarios_padron = %s AND e.idEvaluacion = %s
            """


            cursor.execute(query, (curso_id, padron, id_evaluacion))
            nota = cursor.fetchone()

        if nota is None:
            return jsonify(error_404(f"No se encontró la nota solicitada.")), 404
        return jsonify(nota), 200

    except mysql.connector.Error as e:
        return jsonify(error_500("Error al obtener información de la base de datos: " + str(e))), 500
    finally:
        conn.close()
        cursor.close()





@api_bp.route('/curso/<curso_id>/evaluaciones/<idEvaluacion>/notas', methods=['POST'])
def guardar_nota(curso_id, idEvaluacion):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        data = request.get_json()
        nota = data.get('nota')
        grupal = data.get('id_equipo')
        padron = data.get('padron')

        if not valido_numero(idEvaluacion):
            return jsonify(error_400("El id de la evaluación debe ser un número entero positivo.")), 400
        
        if not valido_numero(curso_id):
            return jsonify(error_400("El id del curso debe ser un número entero positivo.")), 400

        if validar_curso(curso_id) == None:
            return jsonify(error_404(f"No se encontró el curso con id {curso_id}.")), 404
            
        if validar_evaluacion(idEvaluacion) == None:
            return jsonify(error_404(f"No se encontró la evaluación con id {idEvaluacion}.")), 404
        
        if not valido_numero(nota):
            return jsonify(error_400("La nota debe ser un número entero positivo.")), 400
        
        if grupal is not None:

            if not valido_numero(grupal):
                return jsonify(error_400("El id del equipo debe ser un número entero positivo.")), 400
            
            if validar_equipo(grupal) == None:
                return jsonify(error_404(f"No se encontró el equipo con id {grupal}.")), 404

            query_g = """
                INSERT INTO Notas (puntaje, Evaluaciones_idEvaluacion, Equipos_idEquipos)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_g, (nota, idEvaluacion, grupal))
            conn.commit()
            return jsonify({"message": "Nota grupal agregada!"}), 201
        else:

            if validar_id(padron) == None:
                return jsonify(error_404(f"No se encontró al alumno con padrón {padron}.")), 404
            
            if not valido_numero(padron):
                return jsonify(error_400("El padrón debe ser un número entero positivo.")), 400

            query_i = """
                INSERT INTO Notas (puntaje, Evaluaciones_idEvaluacion, Usuarios_padron)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_i, (nota, idEvaluacion, padron))
            conn.commit()
            return jsonify({"message": "Nota individual agregada!"}), 201
        
    except mysql.connector.Error as e:
        return jsonify(error_500("Error al obtener información de la base de datos: " + str(e))), 500
    finally:
        conn.close()
        cursor.close()




@api_bp.route('/curso/<curso_id>/evaluaciones/<id_ev>/notas', methods=['PATCH'])
def actualizar_nota(curso_id, id_ev):

    padron = request.args.get('padron', type=int)

    id_equipo = request.args.get('id_equipo', type=int)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        data = request.get_json()

        nota = data.get('puntaje')

        if not valido_numero(id_ev):
            return jsonify(error_400("El id de la evaluación debe ser un número entero positivo.")), 400
        
        if not valido_numero(curso_id):
            return jsonify(error_400("El id del curso debe ser un número entero positivo.")), 400

        if validar_curso(curso_id) == None:
            return jsonify(error_404(f"No se encontró el curso con id {curso_id}.")), 404

        if validar_evaluacion(id_ev) == None:
            return jsonify(error_404(f"No se encontró la evaluación con id {id_ev}.")), 404

        if nota < 0:
            return jsonify(error_400("El puntaje debe ser un número entero positivo.")), 400
        
        if id_equipo is not None:
            if not valido_numero(id_equipo):
                return jsonify(error_400("El id del equipo debe ser un número entero positivo.")), 400
            
            if validar_equipo(id_equipo) is None:
                return jsonify(error_404(f"No se encontró el equipo con id {id_equipo}.")), 404

            query_g = "UPDATE Notas SET puntaje = %s WHERE Equipos_idEquipos = %s AND Evaluaciones_idEvaluacion = %s"
            cursor.execute(query_g, (nota, id_equipo, id_ev))
            conn.commit()

            return jsonify({"message": "Nota grupal actualizada!"}), 200

        elif padron is not None:
            if not valido_numero(padron):
                return jsonify(error_400("El padrón debe ser un número entero positivo.")), 400

            if validar_id(padron) is None:
                return jsonify(error_404(f"No se encontró al alumno con padrón {padron}.")), 404

            query_i = "UPDATE Notas SET puntaje = %s WHERE Usuarios_padron = %s AND Evaluaciones_idEvaluacion = %s"
            cursor.execute(query_i, (nota, padron, id_ev))
            conn.commit()

            return jsonify({"message": "Nota individual actualizada!"}), 200

        else:
            return jsonify(error_400("Falta el id para actualizar la nota")), 400

    except mysql.connector.Error as e:
        return jsonify(error_500("Error al actualizar la nota: " + str(e))), 500
    finally:
        conn.close()
        cursor.close()
            



