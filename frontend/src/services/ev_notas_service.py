import requests
from src.utils.constants import API_BASE_URL

#----------------------------------------------------------------------------------------------------

def extraer_error(respuesta, msg_defecto):
    "Extrae el mensaje de error."

    try:
        datos = respuesta.json()
        if "errors" in datos and len(datos["errors"]) > 0:
            return datos["errors"][0].get('description', msg_defecto)
        return datos.get('description', msg_defecto)
    except Exception:
        return f"Error crítico en el servidor (Código {respuesta.status_code})."

#----------------------------------------------------------------------------------------------------

def consultar_nota(curso_id, id_ev, id_g, tipo, token):

    "Consume la API dando como resultado una nota o none en caso de ser false."
    
    headers = {"Authorization": f"Bearer {token}"}

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
        respuesta = requests.get(API, headers=headers ,params=query_params, timeout=10)
        if respuesta.status_code == 200:
            return {"datos": respuesta.json(), "error": None, "codigo": 200}
        else:
            
            msg_error = extraer_error(respuesta, "No se pudo obtener la nota solicitada.")
            return {"datos": None, "error": msg_error, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "datos": None, "error": "Error de conexión: El servidor está apagado.", "codigo": 500}
    
#----------------------------------------------------------------------------------------------------

def cargar_nota(curso_id, id_ev, id_g, nota, tipo, token):
    
    "Envía los datos a la API para crear una nueva nota."
    
    API = f"{API_BASE_URL}/notas/cargar"

    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "curso_id": int(curso_id), 
        "id_ev": int(id_ev), 
        "nota": float(nota)
    }

    if tipo == 'padron':
        payload['padron'] = int(id_g)
    else:
        payload['id_equipo'] = int(id_g)
    
    try:
        respuesta = requests.post(API, headers,json=payload, timeout=10)
        if respuesta.status_code in [200, 201]:
            return {"error": None, "codigo": respuesta.status_code}
        else:
            error_api = extraer_error(respuesta, "No se pudo cargar la nota.")
            return {"error": error_api, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "error": "Error de conexión: No se pudo conectar al servidor.", "codigo": 500}
    
#---------------------------------------------------------------------------------------------------

def actualizar_nota(curso_id, id_ev, id_g, nuevo_puntaje, tipo, token):
    
    "Envía los datos a la API para modificar una nota existente."

    API = f"{API_BASE_URL}/notas/editar"

    headers = {"Authorization": f"Bearer {token}"}

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
        respuesta = requests.patch(API, headers=headers ,params=query_params, json=json, timeout=10)
        if respuesta.status_code == 200:
            return {"error": None, "codigo": 200}
        else:
            error_api = extraer_error(respuesta, "No se pudo actualizar la nota.")

            return {"error": error_api, "codigo": respuesta.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"exito": False, "error": "Error crítico: El servidor no responde.", "codigo": 500}
    
#---------------------------------------------------------------------------------------------------

def obtener_cursos_activos():
    
    "Obtiene todos los cursos creados"

    API = f"{API_BASE_URL}/notas/cursos"
    
    try:
        response = requests.get(API)
        response.raise_for_status() 
        data = response.json()
        
        cursos_crudos = data.get("cursos", []) if isinstance(data, dict) else data

        cursos_mapeados = []

        for c in cursos_crudos:
            cursos_mapeados.append({
                "id": c.get("idCurso"), 
                "nombre": c.get("nombre"),
            })
            
        return cursos_mapeados
        
    except requests.RequestException as e:
        print(f"[ERROR] No se pudieron obtener los cursos: {e}")
        return []

#---------------------------------------------------------------------------------------------------

def obtener_evaluacion(curso_id):
    
    "Obt"

    url = f"{API_BASE_URL}/notas/evaluaciones" 
    
    # Si viene un curso_id, lo agregamos como parámetro de consulta
    query_params = {}
    if curso_id:
        query_params['curso_id'] = curso_id
    
    try:
        response = requests.get(url, params=query_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        evaluaciones_crudos = data
        
        if isinstance(data, dict):
            evaluaciones_crudos = data.get("evaluaciones", [])

        evaluaciones_mapeados = []

        for e in evaluaciones_crudos:
            evaluaciones_mapeados.append({
                "id": e.get("idEvaluacion"),
                "desc": e.get("descripcion")
            })
        return evaluaciones_mapeados
        
    except requests.RequestException as e:
        print(f"[ERROR] Error al obtener evaluaciones: {e}")
        return []
