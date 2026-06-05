import requests

url_api = "http://127.0.0.1:3006/api"



def consultar_nota(curso_id, id_ev, id_g, tipo):

    "Consume la API dando como resultado una nota o none en caso de ser false."
    
    API = f"{url_api}/curso/{curso_id}/evaluaciones/{id_ev}/notas"
    
    if tipo == 'padron':
        query_param = {'padron': id_g}
    else:
        query_param = {'id_equipo': id_g}

    try:
        respuesta = requests.get(API, params=query_param, timeout=10)
        if respuesta.status_code == 200:
            return {"datos": respuesta.json(), "error": None, "codigo": 200}
        else:
            msg_error = respuesta.json().get('description', 'No se encontró la calificación con los datos ingresados.')
            return {"datos": None, "error": msg_error, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "datos": None, "error": "Error de conexión: El servidor está apagado.", "codigo": 500}
    


def cargar_nota(curso_id, id_evaluacion, id_g, nota, tipo):
    
    "Envía los datos a la API para crear una nueva nota."
    
    API = f"{url_api}/curso/{curso_id}/evaluaciones/{id_evaluacion}/notas"

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
        if respuesta.status_code == 201:
            return {"error": None, "codigo": 201}
        else:
            error_api = respuesta.json().get('description', 'Error al intentar guardar la nota.')
            return { "error": error_api, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "error": "Error de conexión: No se pudo conectar al servidor.", "codigo": 500}
    


def actualizar_nota(curso_id, id_ev, identificador, nuevo_puntaje, tipo):
    
    "Envía los datos a la API para modificar una nota existente."

    API = f"{url_api}/curso/{curso_id}/evaluaciones/{id_ev}/notas"

    if tipo == 'padron':
        query_param = {'padron': identificador}
    else:
        query_param = {'id_equipo': identificador}

    json = {'puntaje': float(nuevo_puntaje)}
    
    try:
        respuesta = requests.patch(API, params=query_param, json=json, timeout=10)
        if respuesta.status_code == 200:
            return {"error": None, "codigo": 200}
        else:
            error_api = respuesta.json().get('description', 'No se pudo actualizar la nota.')

            return {"error": error_api, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "error": "Error crítico: El servidor no responde.", "codigo": 500}