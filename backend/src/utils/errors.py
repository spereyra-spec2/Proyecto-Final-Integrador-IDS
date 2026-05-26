from flask import jsonify


def error_response(code, message, level="error", description=""):
    return jsonify({
        "error": [{
            "code": code,
            "message": message,
            "level": level,
            "description": description
        }]
    }), code


def not_found(detail):
    return error_response(404, "Petición inválida", "warning", detail)

def conflict(detail):
    return error_response(409, "Conflicto", "warning", detail)

def server_error(detail="Error interno del servidor"):
    return error_response(500, "Error interno", "critical", detail)

def bad_request(detail):
    return error_response(400, "Petición inválida", "warning", detail)

def ok_response(detail):
    return error_response(200, "OK", "success", detail)

def well_response(detail):
    return error_response(201, "Creado", "success", detail)

  
def unauthorized(detail):
    return error_response(401, "No autorizado", "error", detail)

def acceso_denegado(details):
    return error_response(403, "Acceso denegado", "error", details)
