from flask import Flask, Blueprint, jsonify, request, url_for, Response
from db import get_equipo, crear_equipo
from typing import Any
import mysql.connector

equipos_bp = Blueprint("equipos",__name__)

@equipos_bp.route("/api/cursos/<int:curso_id>/equipos", methods = ["GET"])
def obtener_equipos(curso_id: int) -> Response:
    try:
    
        equipos = get_equipo(curso_id)
        
    
        return jsonify(equipos), 200
        
    except Exception as e:
        
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500



@equipos_bp.route("/api/cursos/<int:curso_id>/equipos", methods=["POST"])
def registrar_equipo(curso_id: int) -> Response:
    try:
        data = request.get_json()
        
        if not data or "nombre" not in data or "padrones" not in data:
            return jsonify({"error": "Faltan campos obligatorios: 'nombre' y 'padrones'"}), 400
            
        nombre_equipo = data["nombre"]
        padrones = data["padrones"] 
        
        if not isinstance(padrones, list) or len(padrones) == 0:
            return jsonify({"error": "El campo 'padrones' debe ser una lista no vacía"}), 400

        
        crear_equipo(curso_id, nombre_equipo, padrones)
        
        
        return jsonify({
            "mensaje": "Equipo creado y alumnos vinculados exitosamente",
        }), 201
        
    except mysql.connector.Error as db_err:

        return jsonify({"error": f"Error de base de datos (verifique los padrones): {str(db_err)}"}), 422
    except Exception as e:
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500