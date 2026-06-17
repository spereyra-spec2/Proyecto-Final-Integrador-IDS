import requests
from src.utils.constants import BACKEND_URL_EQUIPOS as BACKEND_URL
from backend.src.db.db import get_connection

def encontrar_equipos_del_alumno_activo(equipos, padron):
    """
    Devuelve los equipos donde el alumno esta Activo.
    """
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

#---------------------------------------------------------------------------------------------

def listar_equipos(curso_id):
    """
    Devuelve la lista de equipos del curso. Si el curso no tiene equipos, devuelve una lista vacía. Si el curso no existe, devuelve None.
    """

    response = requests.get(f"{BACKEND_URL}/{curso_id}/equipos")
    if response.status_code == 204:
        return []
    if response.status_code == 200:
        return response.json()
    raise ValueError(f"Error al obtener equipos: {response.status_code} - {response.text}")

#---------------------------------------------------------------------------------------------

def crear_equipo(curso_id, body):
    """
    Crea un equipo en el curso. El body debe contener un JSON con al menos los campos "nombre" (string) y "padrones" (lista de enteros). Devuelve el equipo creado.
    """
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

#---------------------------------------------------------------------------------------------

def join_equipo_by_code(curso_id, access_code, padron, nombre=None):
    """
    Permite a un alumno unirse a un equipo utilizando el código de acceso. Si el código es correcto, el alumno se une al equipo y se devuelve la información del equipo.
    Si el código es incorrecto o el equipo no existe, se lanza una excepción con un mensaje de error.
    """
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

#---------------------------------------------------------------------------------------------

def actualizar_equipo(curso_id, usuarios_padron, body):
    """
    Actualiza un equipo del curso. El body debe contener un JSON con los campos a actualizar. Devuelve el equipo actualizado.
    """
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

#---------------------------------------------------------------------------------------------

def eliminar_equipo(curso_id, usuarios_padron):
    """
    Elimina un equipo del curso. Devuelve True si el equipo fue eliminado, False en caso contrario.
    """
    response = requests.delete(f"{BACKEND_URL}/{curso_id}/equipos/{usuarios_padron}")

    if response.status_code in (200, 204):
        return True

    try:
        err = response.json().get('errors', [{}])[0]
        msg = err.get('description') or err.get('message') or response.text
    except Exception:
        msg = response.text

    raise ValueError(msg)

#---------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------

def filtrar_equipos_por_nombre_y_codigo(equipos, nombre, access_code):
    """
    Filtra una lista de equipos por nombre y código de acceso. 
    Devuelve el equipo que coincida con ambos criterios, o None si no se encuentra ningún equipo que cumpla con las condiciones.
    """
    nombre = (nombre or "").strip().lower()
    access_code = (access_code or "").strip()

    for eq in equipos:
        eq_nombre = (eq.get("nombre") or "").strip().lower()
        eq_code = (eq.get("access_code") or "").strip()

        if eq_nombre == nombre:
            if eq_code not in ("", None):
                if eq_code != access_code:
                    return None
            return eq

    return None
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
def descargar_reporte_equipos_pdf(token, id_curso, sin_equipo='excluir'):
    url = f"{BACKEND_URL}/{id_curso}/reporte-equipos"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"sin_equipo": sin_equipo}
    try:
        return requests.get(url, headers=headers, params=params, stream=True)
    except requests.exceptions.RequestException:
        return None