from flask import Flask, Blueprint, jsonify, request, url_for, Response
from src.db.db import get_equipos, crear_equipo, delete_equipo, patch_equipo
from src.utils.validaciones import validar_curso_datos, validar_entero
from typing import Any
import mysql.connector
from src.utils.errors import error_response, not_found, bad_request, server_error, conflict

equipos_bp = Blueprint("equipos",__name__)

@equipos_bp.route("/<int:curso_id>/equipos", methods = ["GET"])
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



@equipos_bp.route("/<int:curso_id>/equipos", methods=["POST"])
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
        
        
        return jsonify({"message": "Equipo creado y alumnos vinculados exitosamente",}), 201
        
    except mysql.connector.Error as db_err:

        res, code = bad_request(f"Error de base de datos (verifique los padrones): {str(db_err)}")
        return jsonify(res), code
    except Exception as e:
        res, code = server_error(str(e))
        return jsonify(res), code

@equipos_bp.route("/<int:curso_id>/equipos/<int:usuario_padron>", methods=["PATCH"])
def actualizar_equipo(curso_id, usuario_padron):
    try:
        curso_id = validar_curso_id(curso_id)
        usuario_padron = validar_padron(usuario_padron)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify(bad_request("El body debe ser JSON")), 400

    if not isinstance(data, dict):
        return jsonify(bad_request("El body JSON debe ser un objeto.")), 400

    alumno_padron = data.get("alumno_padron", data.get("padron"))
    activo = data.get("activo")
    evaluacion_id = data.get("evaluacion_id", data.get("tp_id"))

    if alumno_padron is None and activo is not None:
        return jsonify(bad_request("El body debe incluir 'alumno_padron' para cambiar el estado de un alumno.")), 400

    if alumno_padron is not None and (not isinstance(alumno_padron, int) or alumno_padron <= 0):
        return jsonify(bad_request("El padrón del alumno debe ser un número positivo.")), 400

    if activo is not None and activo not in (0, 1):
        return jsonify(bad_request("El campo 'activo' debe ser 0 o 1.")), 400

    if alumno_padron is not None and activo is None:
        return jsonify(bad_request("El body debe incluir 'activo' para cambiar el estado de un alumno.")), 400

    if evaluacion_id is not None and (not isinstance(evaluacion_id, int) or evaluacion_id <= 0):
        return jsonify(bad_request("El ID de la evaluación/TP debe ser un número positivo.")), 400

    if alumno_padron is None and evaluacion_id is None:
        return jsonify(bad_request("El body debe incluir un alumno para agregar/remover o una evaluación/TP.")), 400

    try:
        equipo = patch_equipo(
            curso_id,
            usuario_padron,
            {
                "alumno_padron": alumno_padron,
                "activo": activo,
                "evaluacion_id": evaluacion_id,
            },
        )
        if equipo is None:
            return jsonify(not_found("No existe un equipo activo para ese curso y padrón.")), 404
        return jsonify(equipo), 200
    except ValueError as error:
        return jsonify(bad_request(str(error))), 400
    except Exception as error:
        return jsonify(server_error(error)), 500


@equipos_bp.route("/<int:curso_id>/equipos/<int:usuario_padron>", methods=["DELETE"])
def disolver_equipo(curso_id, usuario_padron):
    try:
        curso_id = validar_curso_id(curso_id)
        usuario_padron = validar_padron(usuario_padron)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400
    try:
        eliminado = delete_equipo(curso_id, usuario_padron)
        if not eliminado:
            return jsonify(not_found("No existe un equipo activo para ese curso y padrón.")), 404

        return jsonify({"message": "Equipo disuelto correctamente."}), 200

    except Exception as e:
        return jsonify(server_error(e)), 500
