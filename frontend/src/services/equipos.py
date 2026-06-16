import requests
from src.utils.constants import BACKEND_URL_EQUIPOS as BACKEND_URL

def encontrar_equipos_del_alumno_activo(equipos, padron):
    res = []
    for equipo in equipos:
        integrantes = equipo.get('integrantes') or []
        for integrante in integrantes:
            pad = integrante.get('padron') if isinstance(integrante, dict) else integrante
            activo = integrante.get('activo') if isinstance(integrante, dict) else 1
            try:
                if int(pad) == int(padron) and int(activo) == 1:
                    res.append(equipo)
                    break
            except Exception:
                continue

    return res

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

    if not isinstance(body["padrones"], list):
        raise ValueError("'padrones' debe ser una lista")

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

def filtrar_equipos_por_nombre_y_codigo(equipos, nombre, access_code):
    nombre = (nombre or "").strip().lower()
    access_code = (access_code or "").strip()

    for eq in equipos:
        eq_nombre = (eq.get("nombre") or "").strip().lower()
        eq_code = (eq.get("access_code") or "").strip()

        if eq_nombre == nombre:
            # si tiene código, lo valida
            if eq_code not in ("", None):
                if eq_code != access_code:
                    return None
            return eq

    return None
#---------------------------------------------------------------------------------------------