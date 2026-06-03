import requests
from ..constants import API_BASE_URL

def respuesta_error(response):
    #devuelve el json de error de la api
    try:
        return response.json()
    except Exception:
        return {'errors': [{'description': f'Error del servidor: HTTP. Código de estado: {response.status_code}'}]}

def error_conexion():
    return {'errors': [{'description': "No se pudo conectar con el servidor. Verificá que la API esté corriendo"}]}

def login(padron, contrasena):
    #retorna {'ok': True, 'token':..., 'padron': {..}, 'rol': {..} }

    try: 
        response = requests.post(
            f'{API_BASE_URL}/auth/login',
            json={'padron': padron, 'contrasena': contrasena},
            timeout= 10
        )

        if response.status_code == 200:
            data = response.json()
            return { 'ok' : True, 'token':data['token'], 'padron': data['padron'], 'rol': data['rol'] }
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response':{'errors': [{'description': f'Error inesperado: {e}'}]}}
            

def contrasena_olvidada(padron):
    try:
        response = requests.post(
            f'{API_BASE_URL}/auth/contrasena_olvidada',
            json={'padron': padron},
            timeout= 30
        )
        if response.status_code == 200:
            return {'ok': True}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response':{'errors': [{'description': f'Error inesperado: {e}'}]}}
    

def resetear_contrasena(token, contrasena):
    try:
        response = requests.patch(
            f'{API_BASE_URL}/auth/resetear_contrasena',
            json={'contrasena': contrasena},
            params={'token': token},
            timeout= 30
        )
        if response.status_code == 200:
            return {'ok': True}
        
        return {'ok': False, 'error_response': respuesta_error(response)}
    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': error_conexion()}
    except Exception as e:
        return {'ok': False, 'error_response':{'errors': [{'description': f'Error inesperado: {e}'}]}}