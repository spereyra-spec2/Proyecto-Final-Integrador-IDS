from flask import jsonify

def error_response(code, message, level="error", description=""):
    return jsonify({
        "errors": [{
            "code": code,
            "message": message,
            "level": level,
            "description": description
        }]
    }), code

def not_found(detail):
    return error_response(404, "No encontrado", "info", str(detail))

def conflict(detail):
    return error_response(409, "Conflicto", "warning", str(detail))

def server_error(detail="Error interno del servidor"):
    return error_response(500, "Error interno", "critical", str(detail))

def bad_request(detail):
    return error_response(400, "Petición inválida", "warning", str(detail))

def acceso_denegado(detail="Acceso denegado"):
    return error_response(403, "Acceso denegado", "error", str(detail))

def acceso_denegado1(details):
    return acceso_denegado(details)

def ok_response(detail):
    return error_response(200, "OK", "success", detail)

def created_response(detail):
    return error_response(201, "Creado", "success", detail)

def unauthorized(detail="No autorizado"):
    return error_response(401, "No autorizado", "error", str(detail))

def unsupported_media_type(detail):
    return error_response(415, "Formato del cuerpo no soportado", "error", str(detail))

def forbidden(detail="Prohibido"):
    return error_response(403, "Prohibido", "error", str(detail))

def unprocessable_entity(detail="Entidad no procesable"):
    return error_response(422, "Entidad no procesable", "error", str(detail))

def no_registrado(padron):
    return error_response(404, "NOT FOUND", "error", f"No se encontró registrado un usuario con el padrón {padron}.")

def contrasena_incorrecta():
    return error_response(401, "UNAUTHORIZED", "error", "Contraseña incorrecta")

def datos_incompletos():
    return error_response(400, "BAD REQUEST", "error", "Falta ingresar datos requeridos")

def datos_incorrectos(dato):
    return error_response(400, "BAD REQUEST", "error", f"Se han introducido datos incorrectos: {dato}")

def ya_existe():
    return error_response(409, "CONFLICT", "error", "Ya existe un usuario con ese padrón")

def error_enviando_correo(e):
    return error_response(500, "SERVER ERROR", "error", str(e))

