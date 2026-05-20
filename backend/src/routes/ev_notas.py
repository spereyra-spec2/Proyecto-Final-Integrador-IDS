from flask import Blueprint, request, jsonify
from mysql.connector import Error
from db import get_conection
    
from src.db.ev_notas_db import validar_id, validar_curso, validar_evaluacion
from src.utils.validar_numeros import valido_numero
from src.utils.errors_ev_notas import error_400, error_404


cursos_bp=Blueprint('cursos', __name__)


@cursos_bp.route('/<curso_id>/evaluaciones/<padron>/<idEvaluacion>/notas', methods=['GET'])
def obtener_nota(curso_id, padron, idEvaluacion):

    conn = get_conection()
    cursor = conn.cursor(dictionary=True)
    try:

        
        if not valido_numero(padron):
            error_400("El padrón debe ser un número entero positivo.")

        if not valido_numero(idEvaluacion):
            error_400("El id de la evaluación debe ser un número entero positivo.")
        
        if not valido_numero(curso_id):
            error_400("El id del curso debe ser un número entero positivo.")

        if validar_id(padron) == None:
            error_404(f"No se encontró al alumno con padrón {padron}.")

        if validar_curso(curso_id) == None:
            error_404(f"No se encontró el curso con id {curso_id}.")
            
        if validar_evaluacion(idEvaluacion) == None:
            error_404(f"No se encontró la evaluación con id {idEvaluacion}.")
        
        

        query = """
            SELECT n.puntaje, e.tipo
            FROM Notas n
            INNER JOIN Evaluaciones e ON n.Evaluaciones_idEvaluacion = e.idEvaluacion
            WHERE e.Curso_idCurso = %s AND n.Usuarios_padron = %s AND e.idEvaluacion = %s
        """


        cursor.execute(query, (curso_id, padron, idEvaluacion))
        nota = cursor.fetchone()

        if nota is None:
            return jsonify({
                "errors": [
                    {
                        "code": "404",
                        "message": "NOT FOUND",
                        "level": "error",
                        "description": f"No se encontró la nota del alumno con padrón {id}."
                    }
                ]
            }), 404
        return jsonify(nota), 200

    except Error as e:
        return jsonify({
            "errors": [
                {
                        "code": "400",
                        "message": "BAD REQUEST",
                        "level": "error",
                        "description": "Error al obtener información de la base de datos: " + str(e)
                    }
                ]
            }), 400
    finally:
        conn.close()
        cursor.close()



@cursos_bp.route('/<curso_id>/evaluaciones/<padron>/<idEvaluacion>/notas', methods=['POST'])
def guardar_nota(curso_id, padron, idEvaluacion):

    conn = get_conection()
    cursor = conn.cursor(dictionary=True)

    try:

        data = request.get_json()
        puntaje = data.get('puntaje')
        grupal = data.get('Equipos_idEquipos')

        if not valido_numero(padron):
            error_400("El padrón debe ser un número entero positivo.")

        if not valido_numero(idEvaluacion):
            error_400("El id de la evaluación debe ser un número entero positivo.")
        
        if not valido_numero(curso_id):
            error_400("El id del curso debe ser un número entero positivo.")

        if validar_id(padron) == None:
            error_404(f"No se encontró al alumno con padrón {padron}.")

        if validar_curso(curso_id) == None:
            error_404(f"No se encontró el curso con id {curso_id}.")
            
        if validar_evaluacion(idEvaluacion) == None:
            error_404(f"No se encontró la evaluación con id {idEvaluacion}.")
        
        if not valido_numero(puntaje):
            error_400("El puntaje debe ser un número entero positivo.")
        
        if grupal is not None:
            query_g = """
                SELECT Equipos_idEquipos FROM Usuarios_has_Equipos ue
                JOIN Equipos eq ON ue.Equipos_idEquipos = eq.idEquipos
                WHERE ue.Usuarios_padron = %s AND eq.Curso_idCurso = %s AND ue.activo = 1
            """
            cursor.execute(query_g, (padron, curso_id))
            equipo = cursor.fetchone()
            if equipo is not None:
                query_g2 = """
                    INSERT INTO Notas (puntaje, Evaluaciones_idEvaluacion, Equipos_idEquipos)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_g2, (puntaje, idEvaluacion, equipo['Equipos_idEquipos']))
                conn.commit()
                return jsonify({"message": "Nota grupal agregada!"}), 201
            else:
                return error_404(f"No se encontró un equipo activo para el alumno con padrón {padron}")
        else:
            query_i = """
                INSERT INTO Notas (puntaje, Evaluaciones_idEvaluacion, Usuarios_padron)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_i, (puntaje, idEvaluacion, padron))
            conn.commit()
            return jsonify({"message": "Nota individual agregada!"}), 201
        

    except Error as e:
        return jsonify({
            "errors": [
                {
                        "code": "400",
                        "message": "BAD REQUEST",
                        "level": "error",
                        "description": "Error al obtener información de la base de datos: " + str(e)
                    }
                ]
            }), 400
    finally:
        conn.close()
        cursor.close()


@cursos_bp.route('/<curso_id>/evaluaciones/<padron>/<idEvaluacion>/notas', methods=['PATCH'])
def actualizar_nota(curso_id, padron, idEvaluacion):

    conn = get_conection()
    cursor = conn.cursor(dictionary=True)

    try:

        data = request.get_json()
        nota = data.get('puntaje')

        if not valido_numero(padron):
            error_400("El padrón debe ser un número entero positivo.")

        if not valido_numero(idEvaluacion):
            error_400("El id de la evaluación debe ser un número entero positivo.")
        
        if not valido_numero(curso_id):
            error_400("El id del curso debe ser un número entero positivo.")

        if validar_id(padron) == None:
            error_404(f"No se encontró al alumno con padrón {padron}.")

        if validar_curso(curso_id) == None:
            error_404(f"No se encontró el curso con id {curso_id}.")
            
        if validar_evaluacion(idEvaluacion) == None:
            error_404(f"No se encontró la evaluación con id {idEvaluacion}.")
        
        if not valido_numero(nota):
            error_400("El puntaje debe ser un número entero positivo.")
        
        query = "UPDATE Notas SET puntaje = %s WHERE Usuarios_padron = %s AND Evaluaciones_idEvaluacion = %s"
        cursor.execute(query, (nota, padron, idEvaluacion))
        conn.commit()

        return jsonify({"message": "Nota actualizada!"}), 200

    except Error as e:
        return jsonify({
            "errors": [
                {
                        "code": "400",
                        "message": "BAD REQUEST",
                        "level": "error",
                        "description": "Error al obtener información de la base de datos: " + str(e)
                    }
                ]
            }), 400
    finally:
        conn.close()
        cursor.close()
        



