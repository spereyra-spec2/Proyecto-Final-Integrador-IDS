import requests
from src.utils.constants import API_BASE_URL





def extraer_error(respuesta, msg_defecto):
    """Extrae el mensaje de error de forma segura, evitando crasheos."""
    try:
        datos = respuesta.json()
        if "errors" in datos and len(datos["errors"]) > 0:
            return datos["errors"][0].get('description', msg_defecto)
        return datos.get('description', msg_defecto)
    except Exception:
        return f"Error crítico en el servidor (Código {respuesta.status_code})."



def consultar_nota(curso_id, id_ev, id_g, tipo):

    "Consume la API dando como resultado una nota o none en caso de ser false."
    
    API = f"{API_BASE_URL}/notas/ver"
    
    query_params = {
        'curso_id': curso_id,
        'id_ev': id_ev
    }
    if tipo == 'padron':
        query_params['padron'] = int(id_g)
    else:
        query_params['id_equipo'] = int(id_g)

    try:
        respuesta = requests.get(API, params=query_params, timeout=10)
        if respuesta.status_code == 200:
            return {"datos": respuesta.json(), "error": None, "codigo": 200}
        else:
            
            msg_error = extraer_error(respuesta, "No se pudo obtener la nota solicitada.")
            return {"datos": None, "error": msg_error, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "datos": None, "error": "Error de conexión: El servidor está apagado.", "codigo": 500}
    


def cargar_nota(curso_id, id_evaluacion, id_g, nota, tipo):
    
    "Envía los datos a la API para crear una nueva nota."
    
    API = f"{API_BASE_URL}/notas/cargar"

    payload = {
        "curso_id": int(curso_id), 
        "id_evaluacion": int(id_evaluacion), 
        "nota": float(nota)
    }

    if tipo == 'padron':
        payload['padron'] = int(id_g)
    else:
        payload['id_equipo'] = int(id_g)
    
    try:
        respuesta = requests.post(API, json=payload, timeout=10)
        if respuesta.status_code in [200, 201]:
            return {"error": None, "codigo": respuesta.status_code}
        else:
            error_api = extraer_error(respuesta, "No se pudo cargar la nota.")
            return {"error": error_api, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "error": "Error de conexión: No se pudo conectar al servidor.", "codigo": 500}
    


def actualizar_nota(curso_id, id_ev, id_g, nuevo_puntaje, tipo):
    
    "Envía los datos a la API para modificar una nota existente."

    API = f"{API_BASE_URL}/notas/editar"

    query_params = {
        'curso_id': curso_id,
        'id_ev': id_ev
    }

    if tipo == 'padron':
        query_params['padron'] = int(id_g)
    else:
        query_params['id_equipo'] = int(id_g)

    json = {'puntaje': float(nuevo_puntaje)}
    
    try:
        respuesta = requests.patch(API, params=query_params, json=json, timeout=10)
        if respuesta.status_code == 200:
            return {"error": None, "codigo": 200}
        else:
            error_api = extraer_error(respuesta, "No se pudo actualizar la nota.")

            return {"error": error_api, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "error": "Error crítico: El servidor no responde.", "codigo": 500}