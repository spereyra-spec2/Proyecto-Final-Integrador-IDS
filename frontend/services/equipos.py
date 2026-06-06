from db import get_equipos, crear_equipo as db_crear_equipo, patch_equipo as db_patch_equipo, delete_equipo as db_delete_equipo
from src.utils.errors import bad_request, not_found

def listar_equipos(curso_id):
    return get_equipos(curso_id)

def crear_equipo(curso_id, body):
    if body is None:
        raise ValueError(bad_request("Debe enviarse un JSON"))

    nombre = body.get("nombre")
    padrones = body.get("padrones")

    if nombre is None:
        raise ValueError("Falta el campo 'nombre'")
    if padrones is None:
        raise ValueError("Falta el campo 'padrones'")
    if not isinstance(padrones, list):
        raise ValueError("'padrones' debe ser una lista")
    if len(padrones) == 0:
        raise ValueError("'padrones' no puede estar vacío")

    db_crear_equipo(curso_id, nombre, padrones)
    return {"message": "Equipo creado correctamente"}


def actualizar_equipo(curso_id, usuarios_padron, body):
    if body is None:
        raise ValueError("Debe enviarse un JSON")

    equipo = db_patch_equipo(curso_id,usuarios_padron,body)
    return equipo


def eliminar_equipo(curso_id, usuarios_padron):
    return db_delete_equipo(curso_id, usuarios_padron)