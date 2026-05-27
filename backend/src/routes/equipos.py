from flask import Blueprint, jsonify, request

from src.db import (
    delete_equipo,
    patch_equipo,
    list_equipos_por_curso,
    create_equipo_por_curso,
    sync_integrantes_por_equipo,
    delete_equipo_por_id,
    list_students_por_curso,
    get_course_info,
    get_equipo_por_id,
)
from src.utils.errors import not_found, server_error, bad_request

equipos_bp = Blueprint("equipos", __name__)


@equipos_bp.route("/<int:curso_id>", methods=["GET"])
def get_curso_info(curso_id):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    try:
        info = get_course_info(curso_id)
        if info is None:
            return jsonify(not_found("Curso no encontrado.")), 404
        return jsonify(info), 200
    except Exception as e:
        return jsonify(server_error(e)), 500


@equipos_bp.route("/<int:curso_id>/students", methods=["GET"])
def listar_alumnos(curso_id):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    try:
        students = list_students_por_curso(curso_id)
        return jsonify({"results": students}), 200
    except Exception as e:
        return jsonify(server_error(e)), 500


@equipos_bp.route("/<int:curso_id>/equipos", methods=["GET"])
def listar_equipos(curso_id):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    try:
        equipos = list_equipos_por_curso(curso_id)
        return jsonify({"results": equipos}), 200
    except Exception as e:
        return jsonify(server_error(e)), 500


@equipos_bp.route("/<int:curso_id>/equipos", methods=["POST"])
def crear_equipo(curso_id):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    data = request.get_json(silent=True)
    if not data or "nombre" not in data:
        return jsonify(bad_request("El body debe incluir 'nombre'")), 400
    nombre = data.get("nombre")
    cupo = data.get("cupo_maximo", 5)
    try:
        equipo = create_equipo_por_curso(curso_id, nombre, cupo)
        return jsonify(equipo), 201
    except Exception as e:
        return jsonify(server_error(e)), 500


@equipos_bp.route("/<int:curso_id>/equipos/<int:equipo_id>", methods=["PATCH"])
def actualizar_equipo_por_id(curso_id, equipo_id):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    if equipo_id <= 0:
        return jsonify(bad_request("El ID del equipo debe ser un número positivo.")), 400
    data = request.get_json(silent=True)
    if not data:
        return jsonify(bad_request("El body debe ser JSON")), 400

    integrantes = data.get("integrantes")
    try:
        if integrantes is not None:
            pads = sync_integrantes_por_equipo(equipo_id, integrantes)
            equipo = get_equipo_por_id(equipo_id)
            if equipo is None:
                return jsonify(not_found("Equipo no encontrado.")), 404
            equipo_out = {
                "id": str(equipo.get("id")),
                "nombre": equipo.get("nombre"),
                "curso_id": equipo.get("curso_id"),
                "codigo_acceso": f"EQ{int(equipo.get('id')):06d}",
                "cupo_maximo": 5,
                "integrantes": pads,
            }
            return jsonify(equipo_out), 200

        return jsonify(bad_request("No hay acciones definidas en el body.")), 400
    except ValueError as error:
        return jsonify(bad_request(str(error))), 400
    except Exception as error:
        return jsonify(server_error(error)), 500


@equipos_bp.route("/<int:curso_id>/equipos/<int:equipo_id>", methods=["DELETE"])
def eliminar_equipo_por_id(curso_id, equipo_id):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    if equipo_id <= 0:
        return jsonify(bad_request("El ID del equipo debe ser un número positivo.")), 400
    try:
        eliminado = delete_equipo_por_id(equipo_id)
        if not eliminado:
            return jsonify(not_found("No existe el equipo.")), 404
        return jsonify({"message": "Equipo eliminado correctamente."}), 200
    except Exception as e:
        return jsonify(server_error(e)), 500


@equipos_bp.route("/<int:curso_id>/equipos/<int:usuarios_padron>", methods=["PATCH"])
def actualizar_equipo(curso_id, usuarios_padron):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    if usuarios_padron <= 0:
        return jsonify(bad_request("El padrón del usuario debe ser un número positivo.")), 400

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
            usuarios_padron,
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


@equipos_bp.route("/<int:curso_id>/equipos/<int:usuarios_padron>", methods=["DELETE"])
def eliminar_equipo(curso_id, usuarios_padron):
    if curso_id <= 0:
        return jsonify(bad_request("El ID del curso debe ser un número positivo.")), 400
    if usuarios_padron <= 0:
        return jsonify(bad_request("El padrón del usuario debe ser un número positivo.")), 400

    try:
        eliminado = delete_equipo(curso_id, usuarios_padron)
        if not eliminado:
            return jsonify(not_found("No existe un equipo activo para ese curso y padrón.")), 404

        return jsonify({"message": "Equipo disuelto correctamente."}), 200

    except Exception as e:
        return jsonify(server_error(e)), 500
