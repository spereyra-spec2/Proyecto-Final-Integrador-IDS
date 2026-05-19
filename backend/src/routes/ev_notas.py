from flask import Blueprint, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from db import get_conection
from src.db.ev_notas_db import validar_id

evaluaciones_bp=Blueprint('evaluaciones', __name__)


@evaluaciones_bp.route('/<int: id>/notas', methods=['GET'])
def obtener_nota_id(int: id):
    conn = get_conection()
    cursor = conn.cursor(dictionary=True)
    
    query = f"SELECT nota from notas WHERE padron = {id}"

    cursor.execute(query)
    nota = cursor.fetchone()

    conn.close()
    cursor.close()

    if validar_id(id) == None:
        return jsonify({
            "errors": [
                {
                    "code": "404",
                    "message": "NOT FOUND",
                    "level": "error",
                    "description": f"No se encontró al alumno con padrón {id}."
                }
            ]
        }), 404
    if not isinstance(id, int) and id <= 0:
        return jsonify({
            "errors": [
                {
                    "code": "400",
                    "message": "BAD REQUEST",
                    "level": "error",
                    "description": "El padrón debe ser un número entero positivo."
                }
            ]
        }), 400

        
    try:
        
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
        return jsonify(nota)
        

    except Error as e:
        return jsonify({
            "errors": [
                {
                    "code": "500",
                    "message": "INTERNAL SERVER ERROR",
                    "level": "error",
                    "description": f"Error al obtener la nota del alumno con padrón {id}: {str(e)}"
                }
            ]
        }), 500

@evaluaciones_bp.route('/<int:id>/notas', methods=['POST'])
def agregar_nota(int: id):
    conn = get_conection()
    cursor = conn.cursor(dictionary=True)

    data = request.get_json()
    nota = data.get('nota')

    query = f"INSERT INTO notas (padron, nota) VALUES ({id}, {nota})"

    if validar_id(id) == None:
        return jsonify({
            "errors": [
                {
                    "code": "404",
                    "message": "NOT FOUND",
                    "level": "error",
                    "description": f"No se encontró al alumno con padrón {id}."
                }
            ]
        }), 404
    if not isinstance(id, int) and id <= 0:
        return jsonify({
            "errors": [
                {
                    "code": "400",
                    "message": "BAD REQUEST",
                    "level": "error",
                    "description": "El padrón debe ser un número entero positivo."
                }
            ]
        }), 400
    
    try:
        cursor.execute(query)
        conn.commit()

        return jsonify({
            "message": f"Nota agregada exitosamente para el alumno con padrón {id}."
        }), 201

    except Error as e:
        return jsonify({
            "errors": [
                {
                    "code": "500",
                    "message": "INTERNAL SERVER ERROR",
                    "level": "error",
                    "description": f"Error al agregar la nota del alumno con padrón {id}: {str(e)}"
                }
            ]
        }), 500

    finally:
        conn.close()
        cursor.close()

