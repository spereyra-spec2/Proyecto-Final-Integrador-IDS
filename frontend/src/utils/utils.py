from flask import session

def usuario_actual():
    if 'token' not in session:
        return None
    return {
        'token': session['token'],
        'padron': session['padron'],
        'rol': session['rol']
    }

#---------------------------------------------------------------------------------------------

def guardar_sesion(token, padron, rol):
    #persiste el token y el usuario en la sesión de Flask
    session['token'] = token
    session['padron'] = padron
    session['rol'] = rol

#--------------------------------------------------------------------------------------------

def extraer_mensaje_error(api_response):
    errores = (api_response or {}).get('errors', [])
    return [e.get('description') or e.get('message') or 'Error desconocido' for e in errores]

#-----------------------------------------------------------------------------------------------  

def limpiar_sesion() -> None:
    """Borra todos los datos de autenticacion de la sesion."""
    session.pop('token', None)
    session.pop('padron', None)
    session.pop('rol', None)

#---------------------------------------------------------------------------------------------

def verificar_docente_autenticado():
    usuario = usuario_actual()
    if not usuario or usuario.get('rol') != 'Docente':
        return None
    return usuario

#---------------------------------------------------------------------------------------------

def validar_curso_id(curso_id):
    try:
        cid = int(curso_id)
        if cid <= 0:
            raise ValueError('El curso_id debe ser un número entero positivo.')
        return cid
    except Exception:
        raise ValueError('El curso_id debe ser un número entero válido.')

#---------------------------------------------------------------------------------------------

def validar_padron(padron):
    try:
        p = int(padron)
        if p <= 0:
            raise ValueError('El padrón debe ser un número entero positivo.')
        return p
    except Exception:
        raise ValueError('El padrón debe ser un número entero válido.')
    
#---------------------------------------------------------------------------------------------

def validar_equipo_id(equipo_id):
    try:
        eid = int(equipo_id)
        if eid <= 0:
            raise ValueError('El equipo_id debe ser un número entero positivo.')
        return eid
    except Exception:
        raise ValueError('El equipo_id debe ser un número entero válido.')

