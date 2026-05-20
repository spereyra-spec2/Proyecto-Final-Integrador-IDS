from flask import request, jsonify

def validar_email_fiuba(email):
    """
    Valida que el email contenga un '@', tenga texto antes del '@' 
    y el dominio sea exactamente 'fi.uba.ar'.
    """
    usuario = ""
    dominio = ""
    
    if email and '@' in email:
        partes = email.rsplit('@', 1)
        usuario = partes[0].strip()
        dominio = partes[1].strip()
        
    return usuario != '' and dominio == 'fi.uba.ar'

#------------------------
def error_response(code, message, level="error", description=""):
    return {
        "error": [{
            "code": code,
            "message": message,
            "level": level,
            "description": description
        }]
    }, code


def not_found(detail):
    return error_response(404, "Petición inválida", "warning", detail)

def conflict(detail):
    return error_response(409, "Conflicto", "warning", detail)

def server_error(detail="Error interno del servidor"):
    return error_response(500, "Error interno", "critical", detail)

def bad_request(detail):
    return error_response(400, "Petición inválida", "warning", detail)

