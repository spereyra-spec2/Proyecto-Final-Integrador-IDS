import requests
import logging
from src.utils.constants import API_BASE_URL

logger = logging.getLogger(__name__)

def obtener_evaluaciones(idEvaluacion=None):
    """Obtiene evaluaciones del backend"""
    try:
        if idEvaluacion:
            url = f"{API_BASE_URL}/evaluaciones/{idEvaluacion}"
            respuesta = requests.get(url)
            if respuesta.status_code == 200:
                return respuesta.json()
            elif respuesta.status_code == 404:
                return None
            else:
                logger.error(f"Error {respuesta.status_code}: {respuesta.text}")
                return None
        else:
            url = f"{API_BASE_URL}/evaluaciones"
            respuesta = requests.get(url)
            if respuesta.status_code == 200:
                return respuesta.json()
            else:
                logger.error(f"Error {respuesta.status_code}: {respuesta.text}")
                return []
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión con la API {API_BASE_URL}")
        return [] if not idEvaluacion else None
    except Exception as e:
        logger.error(f"Error al obtener evaluaciones: {str(e)}")
        return [] if not idEvaluacion else None

def crear_evaluacion(tipo: str, descripcion: str, fecha: str, curso_id: int) -> dict:
    """Crea una nueva evaluación en el backend"""
    try:
        # El backend espera 'Curso_idCurso' en lugar de 'curso_id'
        payload = {
            'tipo': tipo,
            'descripcion': descripcion,
            'fecha': fecha,
            'Curso_idCurso': curso_id  # Importante: usar el nombre exacto que espera el backend
        }
        
        respuesta = requests.post(
            f"{API_BASE_URL}/evaluaciones",
            json=payload
        )
        
        if respuesta.status_code == 201:
            data = respuesta.json()
            return {
                'ok': True,
                'success': True,
                'message': data.get('message', 'Evaluación creada exitosamente'),
                'idEvaluacion': data.get('idEvaluacion')
            }
        else:
            error_data = respuesta.json()
            error_msg = error_data.get('error', 'Error al crear evaluación')
            return {
                'ok': False,
                'success': False,
                'message': error_msg,
                'errors': [error_msg]
            }
    except Exception as e:
        return {
            'ok': False,
            'success': False,
            'message': f'Error de conexión: {str(e)}',
            'errors': [f'Error de conexión: {str(e)}']
        }
    
def actualizar_evaluacion(idEvaluacion: int, tipo: str, descripcion: str, fecha: str, curso_id: int) -> dict:
    """Actualiza una evaluación existente en el backend"""
    try:
        payload = {
            'tipo': tipo,
            'descripcion': descripcion,
            'fecha': fecha,
            'Curso_idCurso': curso_id
        }
        
        respuesta = requests.put(
            f"{API_BASE_URL}/evaluaciones/{idEvaluacion}",
            json=payload
        )
        
        if respuesta.status_code == 200:
            data = respuesta.json()
            return {
                'ok': True,
                'success': True,
                'message': data.get('message', 'Evaluación actualizada exitosamente')
            }
        else:
            error_data = respuesta.json()
            error_msg = error_data.get('error', 'Error al actualizar evaluación')
            return {
                'ok': False,
                'success': False,
                'message': error_msg,
                'errors': [error_msg]
            }
    except Exception as e:
        return {
            'ok': False,
            'success': False,
            'message': f'Error de conexión: {str(e)}',
            'errors': [f'Error de conexión: {str(e)}']
        }