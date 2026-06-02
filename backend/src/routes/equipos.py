from flask import Flask, Blueprint, jsonify, request, url_for, Response
from backend.db import get_equipos, crear_equipo
from typing import Any
import mysql.connector
from backend.src.utils.errors import error_response, not_found, bad_request, server_error, conflict

equipos_bp = Blueprint("equipos",__name__)

@equipos_bp.route("/api/cursos/<int:curso_id>/equipos", methods = ["GET"])
def obtener_equipos(curso_id: int) -> Response:
    try:
    
        equipos = get_equipos(curso_id)
        if not equipos: 
            res, code = not_found("curso o equipos")
            return jsonify(res), code
        
    
        return jsonify(equipos), 200
        
    except Exception as e:
        
        res, code = server_error(str(e))
        return jsonify(res), code



@equipos_bp.route("/api/cursos/<int:curso_id>/equipos", methods=["POST"])
def registrar_equipo(curso_id: int) -> Response:
    try:
        data = request.get_json()
        
        if not data or "nombre" not in data or "padrones" not in data:
            res, code = bad_request("Faltan campos obligatorios: 'nombre' y 'padrones'")
            return jsonify(res), code
        
            
        nombre_equipo = data["nombre"]
        padrones = data["padrones"] 
        
        if not isinstance(padrones, list) or len(padrones) == 0:
            res, code = bad_request("El campo 'padrones' debe ser una lista no vacía")
            return jsonify(res), code

        
        crear_equipo(curso_id, nombre_equipo, padrones)
        
        
        return jsonify({
            "message": "Equipo creado y alumnos vinculados exitosamente",
        }), 201
        
    except mysql.connector.Error as db_err:

        res, code = bad_request(f"Error de base de datos (verifique los padrones): {str(db_err)}")
        return jsonify(res), code
    except Exception as e:
        res, code = server_error(str(e))
        return jsonify(res), code