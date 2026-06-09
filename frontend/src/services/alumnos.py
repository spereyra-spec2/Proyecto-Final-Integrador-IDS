import requests
from src.utils.constants import API_BASE_URL
from .auth import respuesta_error, error_conexion

#---------------------------------------------------------------------------------------------------------

def actualizar_alumno(token, id_curso, padron, nombres, mail, estado):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        if nombres: payload["nombres"] = nombres
        if mail: payload["mail"] = mail
        if estado is not None: payload["estado"] = int(estado)

        response = requests.patch(
            f'{API_BASE_URL}/cursos/{id_curso}/alumnos/{padron}',
            headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            return {'ok': True}
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error: {e}'}]}}

#---------------------------------------------------------------------------------------------------------

def baja_logica_alumno(token, id_curso, padron):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(
            f'{API_BASE_URL}/cursos/{id_curso}/alumnos/{padron}',
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return {'ok': True}
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error: {e}'}]}}
    
#---------------------------------------------------------------------------------------------------------

def obtener_ficha_alumno(token, id_curso, padron):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f'{API_BASE_URL}/cursos/{id_curso}/alumnos/{padron}',
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return {'ok': True, 'alumno': response.json().get('alumno', {})}
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error: {e}'}]}}

#---------------------------------------------------------------------------------------------------------

def obtener_alumnos(token, id_curso, estado_filtro=None):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {}
        if estado_filtro is not None:
            params['estado'] = estado_filtro

        response = requests.get(
            f'{API_BASE_URL}/cursos/{id_curso}/alumnos',
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return {'ok': True, 'alumnos': data.get('alumnos', [])}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}

#---------------------------------------------------------------------------------------------------------

def agregar_alumno(token, id_curso, padron, nombres, mail):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"padron": int(padron), "nombres": nombres, "mail": mail}
        response = requests.post(
            f'{API_BASE_URL}/cursos/{id_curso}/alumnos',
            headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code == 200 or response.status_code == 201:
            return {'ok': True}
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error: {e}'}]}}

#---------------------------------------------------------------------------------------------------------

def importar_csv(token, id_curso, archivo_file):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        files = {'file': (archivo_file.filename, archivo_file.stream, archivo_file.mimetype)}
        response = requests.post(
            f'{API_BASE_URL}/cursos/{id_curso}/alumnos/importar',
            headers=headers,
            files=files,
            timeout=20
        )
        if response.status_code == 200 or response.status_code == 201:
            return {'ok': True}
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error: {e}'}]}}

#---------------------------------------------------------------------------------------------------------

def obtener_alumno_por_padron(token, id_curso, padron):
    """
    GET /api/cursos/<idCurso>/alumnos/<padron>
    Consulta la API del backend para traer los datos técnicos de un alumno específico.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f'{API_BASE_URL}/cursos/{id_curso}/alumnos/{padron}',
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return {'ok': True, 'alumno': data.get('alumno', {})}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}