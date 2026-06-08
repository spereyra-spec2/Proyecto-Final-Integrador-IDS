from flask import Blueprint, jsonify, request
from backend.src.utils.errors import bad_request, not_found 
from backend.src.utils.validaciones import validar_curso_id, validar_padron
from frontend.src.services.equipos import listar_equipos, crear_equipo, actualizar_equipo, eliminar_equipo

equipos_bp = Blueprint('equipos', __name__)

@equipos_bp.route('/<curso_id>/equipos', methods=['GET'])
def get_equipos(curso_id):

    try:
        curso_id = validar_curso_id(curso_id)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400

    equipos = listar_equipos(curso_id)

    if not equipos:
        return '', 204

    return jsonify(equipos)


@equipos_bp.route('/<curso_id>/equipos', methods=['POST'])
def post_equipo(curso_id):

    try:
        curso_id = validar_curso_id(curso_id)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400

    body = request.get_json(silent=True)

    try:
        equipo = crear_equipo(curso_id, body)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400

    return jsonify(equipo), 201


@equipos_bp.route('<int:curso_id>/equipos/<int:usuario_padron>', methods=['PATCH'])
def patch_equipo_route(curso_id, usuario_padron):

    try:
        curso_id = validar_curso_id(curso_id)
        usuario_padron = validar_padron(usuario_padron)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400

    body = request.get_json(silent=True)

    try:
        equipo = actualizar_equipo(curso_id, usuario_padron, body)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400

    if not equipo:
        return jsonify(not_found(f"No existe un equipo asociado al padrón '{usuario_padron}'")), 404

    return jsonify(equipo) , 200


@equipos_bp.route('<int:curso_id>/equipos/<int:usuario_padron>', methods=['DELETE'])
def delete_equipo_route(curso_id, usuario_padron):

    try:
        curso_id = validar_curso_id(curso_id)
        usuario_padron = validar_padron(usuario_padron)
    except ValueError as e:
        return jsonify(bad_request(str(e))), 400

    eliminado = eliminar_equipo(curso_id, usuario_padron)

    if not eliminado:
        return jsonify(not_found(f"No existe un equipo asociado al padrón '{usuario_padron}'")), 404

    return jsonify({"message": "Equipo eliminado correctamente"}) , 200