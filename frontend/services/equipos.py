from db import get_equipos, crear_equipo as db_crear_equipo, patch_equipo as db_patch_equipo, delete_equipo as db_delete_equipo
from src.utils.errors import bad_request, not_found
import requests

BACKEND_URL = "http://localhost:5001/api/cursos"

def listar_equipos(curso_id):
    response = requests.get(f"{BACKEND_URL}/{curso_id}/equipos")
    if response.status_code == 204:
        return []
    if response.status_code == 200:
        return response.json()
    return []

def crear_equipo(curso_id, body):
    if body is None:
        raise ValueError("Debe enviarse un JSON")

    if "nombre" not in body or "padrones" not in body:
        raise ValueError("Faltan campos obligatorios ('nombre' o 'padrones')")

    response = requests.post(f"{BACKEND_URL}/{curso_id}/equipos", json=body)
    
    if response.status_code == 201:
        return response.json()
    else:
        error_msg = response.json().get("message", "Error al crear el equipo en el backend")
        raise ValueError(error_msg)

def actualizar_equipo(curso_id, usuarios_padron, body):
    if body is None:
        raise ValueError("Debe enviarse un JSON")
        
    response = requests.patch(f"{BACKEND_URL}/{curso_id}/equipos/{usuarios_padron}", json=body)
    if response.status_code == 200:
        return response.json()
    return None

def eliminar_equipo(curso_id, usuarios_padron):
    response = requests.delete(f"{BACKEND_URL}/{curso_id}/equipos/{usuarios_padron}")
    if response.status_code == 200:
        return True
    return False
'''
def actualizar_equipo(curso_id, usuarios_padron, body):
    if body is None:
        raise ValueError("Debe enviarse un JSON")

    equipo = db_patch_equipo(curso_id,usuarios_padron,body)
    return equipo


def eliminar_equipo(curso_id, usuarios_padron):
    return db_delete_equipo(curso_id, usuarios_padron)
'''