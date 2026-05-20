from flask import Blueprint, jsonify, request

from db import get_equipo, put_equipo, delete_equipo
from utils.errors import not_found, server_error, bad_request

equipos_bp = Blueprint("equipos", __name__)

@equipos_bp.route('/<int:padron>', methods=['PUT'])
def actualizar (padron):


@equipos_bp.route('/<int:padron>', methods=['DELETE'])
def eliminar_equipo(id):
