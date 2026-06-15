import requests
from src.utils.constants import API_BASE_URL
from .auth import respuesta_error, error_conexion

def obtener_evaluaciones(token, idEvaluacion=None, curso_id=None):
    """Obtiene evaluaciones del backend"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        if idEvaluacion:
            response = requests.get(
                f'{API_BASE_URL}cursos/{curso_id}/evaluaciones/{idEvaluacion}',
                headers=headers,
                timeout=10
            )
        else:
            response = requests.get(
                f'{API_BASE_URL}cursos/{curso_id}/evaluaciones',
                headers=headers,
                timeout=10
            )
        
        if response.status_code == 200:
            data = response.json()
            return {'ok': True, 'evaluaciones': data}
        elif response.status_code == 404:
            return {'ok': False, 'error_response': {'errors': [{'description': 'Evaluación no encontrada'}]}}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}



def crear_evaluacion(token, tipo, descripcion, fecha, curso_id):
    """Crea una nueva evaluación en el backend"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "tipo": tipo,
            "descripcion": descripcion,
            "fecha": fecha,
            "Curso_idCurso": curso_id
        }
        
        response = requests.post(
            f'{API_BASE_URL}cursos/{curso_id}/evaluaciones',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            return {'ok': True, 'message': data.get('message', 'Evaluación creada exitosamente'), 'idEvaluacion': data.get('idEvaluacion')}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}



def actualizar_evaluacion(token, idEvaluacion, tipo=None, descripcion=None, fecha=None, curso_id=None):
    """Actualiza una evaluación existente en el backend (solo campos proporcionados)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {}
        if tipo is not None:
            payload["tipo"] = tipo
        if descripcion is not None:
            payload["descripcion"] = descripcion
        if fecha is not None:
            payload["fecha"] = fecha
        if curso_id is not None:
            payload["Curso_idCurso"] = curso_id
        
        if not payload:
            return {'ok': False, 'error_response': {'errors': [{'description': 'No hay campos para actualizar'}]}}
        
        response = requests.put(
            f'{API_BASE_URL}cursos/{curso_id}/evaluaciones/{idEvaluacion}',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {'ok': True, 'message': data.get('message', 'Evaluación actualizada exitosamente')}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}


def eliminar_evaluacion(token, idEvaluacion, curso_id):
    """Elimina una evaluación del backend"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.delete(
            f'{API_BASE_URL}cursos/{curso_id}/evaluaciones/{idEvaluacion}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'ok': True, 'message': 'Evaluación eliminada exitosamente'}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}