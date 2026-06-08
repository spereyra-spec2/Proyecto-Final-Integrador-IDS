import requests
from src.utils.constants import API_BASE_URL
from .auth import respuesta_error, error_conexion

def actualizar_curso(token, id_curso, nombre, codigo, cuatrimestre, descripcion):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        if nombre: payload["nombre"] = nombre
        if codigo: payload["codigo"] = codigo
        if cuatrimestre: payload["cuatrimestre"] = cuatrimestre
        if descripcion: payload["descripcion"] = descripcion

        response = requests.patch(
            f'{API_BASE_URL}/cursos/{id_curso}',
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
    
    # En src/services/cursos.py cambia el nombre a:
def obtener_cursos(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f'{API_BASE_URL}/cursos',
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return {'ok': True, 'cursos': data.get('cursos', [])}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}
    
# En src/services/cursos.py asegurate de que se llame:
def crear_curso(token, nombre, codigo, cuatrimestre, descripcion):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "nombre": nombre,
            "codigo": codigo,
            "cuatrimestre": cuatrimestre,
            "descripcion": descripcion
        }
        response = requests.post(
            f'{API_BASE_URL}/cursos',
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
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}  


def eliminar_curso(token, id_curso):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(
            f'{API_BASE_URL}/cursos/{id_curso}',
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
          