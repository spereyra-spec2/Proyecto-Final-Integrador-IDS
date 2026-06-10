import requests

BACKEND_URL = "http://localhost:3006/api/cursos"

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
        try:
            err = response.json().get('errors', [{}])[0]
            msg = err.get('description') or err.get('message') or str(response.text)
        except Exception:
            msg = str(response.text)
        raise ValueError(msg)


def join_equipo_by_code(curso_id, access_code, padron, nombre=None):
    payload = {"access_code": access_code, "padron": padron}
    if nombre:
        payload['nombre'] = nombre
    response = requests.post(f"{BACKEND_URL}/{curso_id}/equipos/join", json=payload)
    if response.status_code in (200,201):
        return response.json()
    try:
        err = response.json().get('errors', [{}])[0]
        msg = err.get('description') or err.get('message') or response.text
    except Exception:
        msg = response.text
    raise ValueError(msg)

def actualizar_equipo(curso_id, usuarios_padron, body):
    if body is None:
        raise ValueError("Debe enviarse un JSON")
        
    response = requests.patch(f"{BACKEND_URL}/{curso_id}/equipos/{usuarios_padron}", json=body)
    if response.status_code == 200:
        return response.json()
    try:
        err = response.json().get('errors', [{}])[0]
        msg = err.get('description') or err.get('message') or response.text
    except Exception:
        msg = response.text
    raise ValueError(msg)

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