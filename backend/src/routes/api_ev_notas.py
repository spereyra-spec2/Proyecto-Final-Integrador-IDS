from flask import Blueprint, request, jsonify
import mysql.connector
from src.db.db import get_connection
    
from src.db.ev_notas_db import validar_id, validar_curso, validar_evaluacion, validar_equipo
from src.utils.validar_numeros import valido_numero
from src.utils.errors import bad_request, not_found, server_error

ev_notas_bp=Blueprint('api/notas', __name__)


@ev_notas_bp.route('/ver', methods=['GET'])
def obtener_nota():

    padron = request.args.get('padron', type=int)
    id_equipo = request.args.get('id_equipo', type=int)
    curso_id = request.args.get('curso_id')
    id_evaluacion = request.args.get('id_ev')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:

        if not valido_numero(id_evaluacion):
            return jsonify(bad_request("El id de la evaluación debe ser un número entero positivo.")), 400
        
        if not valido_numero(curso_id):
            return jsonify(bad_request("El id del curso debe ser un número entero positivo.")), 400

        if validar_curso(curso_id) == None:
            return not_found(f"No se encontró el curso con id {curso_id}.")
            
        if validar_evaluacion(id_evaluacion) == None:
            return not_found(f"No se encontró la evaluación con id {id_evaluacion}.")
        
        nota = None
        
        if id_equipo:
            
            if not valido_numero(id_equipo):
                return jsonify(bad_request("El id del equipo debe ser un numero entero positivo.")), 400
            
            if validar_equipo(id_equipo) == None:
                return not_found(f"No se encontró el equipo con id {id_equipo}.")

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
                return jsonify(bad_request("El padrón debe ser un número entero positivo.")), 400

            if validar_id(padron) == None:
                return not_found(f"No se encontró al alumno con padrón {padron}.")

            query = """
                SELECT n.puntaje, e.tipo
                FROM Notas n
                INNER JOIN Evaluaciones e ON n.Evaluaciones_idEvaluacion = e.idEvaluacion
                WHERE e.Curso_idCurso = %s AND n.Usuarios_padron = %s AND e.idEvaluacion = %s
            """


            cursor.execute(query, (curso_id, padron, id_evaluacion))
            nota = cursor.fetchone()

        if nota is None:
            return not_found(f"No se encontró la nota solicitada.")
        return jsonify(nota), 200

    except mysql.connector.Error as e:
        return jsonify(server_error("Error al obtener información de la base de datos: " + str(e))), 500
    finally:
        conn.close()
        cursor.close()





@ev_notas_bp.route('/cargar', methods=['POST'])
def guardar_nota():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        data = request.get_json()
        nota = data.get('nota')
        grupal = data.get('id_equipo')
        padron = data.get('padron')
        curso_id = data.get('curso_id')
        id_ev = data.get('id_ev')

        if not valido_numero(id_ev):
            return jsonify(bad_request("El id de la evaluación debe ser un número entero positivo.")), 400
        
        if not valido_numero(curso_id):
            return jsonify(bad_request("El id del curso debe ser un número entero positivo.")), 400

        if validar_curso(curso_id) == None:
            return not_found(f"No se encontró el curso con id {curso_id}.")
            
        if validar_evaluacion(id_ev) == None:
            return not_found(f"No se encontró la evaluación con id {id_ev}.")
        
        if not valido_numero(nota):
            return jsonify(bad_request("La nota debe ser un número entero positivo.")), 400
        
        veri_id_ev = "SELECT idEvaluacion FROM Evaluaciones WHERE idEvaluacion = %s AND Curso_idCurso = %s"
        cursor.execute(veri_id_ev, (id_ev, curso_id))
        id_ev_valido = cursor.fetchone()

        if id_ev_valido is None:
            return jsonify(bad_request(f"Inconsistencia: La evaluación {id_ev} no pertenece al curso {curso_id}.")), 400
        
        if grupal is not None:

            if not valido_numero(grupal):
                return jsonify(bad_request("El id del equipo debe ser un número entero positivo.")), 400
            
            if validar_equipo(grupal) == None:
                return not_found(f"No se encontró el equipo con id {grupal}.")

            query_g = """
                INSERT INTO Notas (puntaje, Evaluaciones_idEvaluacion, Equipos_idEquipos)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_g, (nota, id_ev, grupal))
            conn.commit()
            return jsonify({"message": "Nota grupal agregada!"}), 201
        else:

            if validar_id(padron) == None:
                return not_found(f"No se encontró al alumno con padrón {padron}.")
            
            if not valido_numero(padron):
                return jsonify(bad_request("El padrón debe ser un número entero positivo.")), 400

            query_i = """
                INSERT INTO Notas (puntaje, Evaluaciones_idEvaluacion, Usuarios_padron)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_i, (nota, id_ev, padron))
            conn.commit()
            return jsonify({"message": "Nota individual agregada!"}), 201
        
    except mysql.connector.Error as e:
        return jsonify(server_error("Error al obtener información de la base de datos: " + str(e))), 500
    finally:
        conn.close()
        cursor.close()




@ev_notas_bp.route('/editar', methods=['PATCH'])
def actualizar_nota():

    padron = request.args.get('padron', type=int)
    curso_id = request.args.get('curso_id')
    id_ev = request.args.get('id_ev')
    id_equipo = request.args.get('id_equipo', type=int)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        data = request.get_json()

        nota = data.get('puntaje')

        if not valido_numero(id_ev):
            return jsonify(bad_request("El id de la evaluación debe ser un número entero positivo.")), 400
        
        if not valido_numero(curso_id):
            return jsonify(bad_request("El id del curso debe ser un número entero positivo.")), 400

        if validar_curso(curso_id) == None:
            return not_found(f"No se encontró el curso con id {curso_id}.")

        if validar_evaluacion(id_ev) == None:
            return not_found(f"No se encontró la evaluación con id {id_ev}.")

        if nota < 0:
            return jsonify(bad_request("El puntaje debe ser un número entero positivo.")), 400
        
        veri_id_ev = "SELECT idEvaluacion FROM Evaluaciones WHERE idEvaluacion = %s AND Curso_idCurso = %s"
        cursor.execute(veri_id_ev, (id_ev, curso_id))
        id_ev_valido = cursor.fetchone()

        if id_ev_valido is None:
            return jsonify(bad_request(f"Inconsistencia: La evaluación {id_ev} no pertenece al curso {curso_id}.")), 400
        
        if id_equipo is not None:
            if not valido_numero(id_equipo):
                return jsonify(bad_request("El id del equipo debe ser un número entero positivo.")), 400
            
            if validar_equipo(id_equipo) is None:
                return not_found(f"No se encontró el equipo con id {id_equipo}.")

            query_g = "UPDATE Notas SET puntaje = %s WHERE Equipos_idEquipos = %s AND Evaluaciones_idEvaluacion = %s"
            cursor.execute(query_g, (nota, id_equipo, id_ev))
            conn.commit()

            return jsonify({"message": "Nota grupal actualizada!"}), 200

        elif padron is not None:
            if not valido_numero(padron):
                return jsonify(bad_request("El padrón debe ser un número entero positivo.")), 400

            if validar_id(padron) is None:
                return not_found(f"No se encontró al alumno con padrón {padron}.")

            query_i = "UPDATE Notas SET puntaje = %s WHERE Usuarios_padron = %s AND Evaluaciones_idEvaluacion = %s"
            cursor.execute(query_i, (nota, padron, id_ev))
            conn.commit()

            return jsonify({"message": "Nota individual actualizada!"}), 200

        else:
            return jsonify(bad_request("Falta el id para actualizar la nota")), 400

    except mysql.connector.Error as e:
        return jsonify(server_error("Error al actualizar la nota: " + str(e))), 500
    finally:
        conn.close()
        cursor.close()
            
@ev_notas_bp.route('/cursos', methods=['GET'])
def get_cursos_publicos():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT idCurso, nombre FROM Curso"

        cursor.execute(query)
        cursos = cursor.fetchall()
        
        return jsonify({"cursos": cursos}), 200
        
    except Exception as e:
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@ev_notas_bp.route('/evaluaciones', methods=['GET'])
def get_tipos_evaluacion_publicos():
    curso_id = request.args.get('curso_id', type=int)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if curso_id:
            query = "SELECT idEvaluacion, descripcion FROM Evaluaciones WHERE Curso_idCurso = %s"
            cursor.execute(query, (curso_id,))
        else:
            query = "SELECT idEvaluacion, descripcion FROM Evaluaciones"
            cursor.execute(query)
            
        evaluacioes = cursor.fetchall()
        return jsonify({"evaluaciones": evaluacioes}), 200
        
    except Exception as e:
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



