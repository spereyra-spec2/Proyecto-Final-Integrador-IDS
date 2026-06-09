import requests
import logging
from src.utils.constants import API_BASE_URL
logger = logging.getLogger(__name__)

#----------------------------------------------------------------------------------------------------

def obtener_evaluaciones(idEvaluacion) -> dict:

    evaluaciones = {}
    try:
        respuesta = requests.get(f"{API_BASE_URL}/api/evaluaciones/{idEvaluacion}")
        evaluaciones = respuesta.json() 
        if respuesta.status_code == 200:
            evaluaciones = respuesta.json()
    
    except requests.exceptions.ConnectionError:
        logger.error("Error de conexión con la API {BACK_URL}")
    
    
    except Exception as e:
        logger.error(f"Error al obtener evaluacion {idEvaluacion}: {str(e)}")

    return evaluaciones

#------------------------------------------------------------------------------------------------------------

def crear_evaluacion(tipo:str, descripcion:str, fecha:str, curso_id:int) -> dict:
    try:
        respuesta = requests.post(
            f"{API_BASE_URL}/api/evaluaciones",
            json={
                'tipo': tipo,
                'descripcion': descripcion,
                'fecha': fecha,
                'Curso_idCurso': curso_id
            }
        )
        
        if respuesta.status_code in [200, 201]:
            return {'success': True, 'message': 'Evaluación creada exitosamente'}
        else:
            return {'success': False, 'message': 'Error al crear evaluación'}
    except Exception as e:
        return {'success': False, 'message': f'Error de conexión: {str(e)}'}