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

def well_response(detail):
    return error_response(201, "Creado", "success", detail)

  
def unauthorized(detail):
    return error_response(401, "No autorizado", "error", detail)



def unsupported_media_type(detail):
    return error_response(415, "Formato del cuerpo no soportado", "error", detail)


def forbidden(detail):
    return error_response(403, "Prohibido", "error", detail)

def unprocessable_entity(detail):
    return error_response(422, "Entidad no procesable", "error", detail)
def conflict(detail="Conflicto"):
    return error_response(409, "Conflicto", "warning", detail)

def forbidden(detail="Acceso Denegado"):
    return error_response(403, "Usted no tiene acceso al recurso solicitado", "warning", detail)

def server_error(e):
    return jsonify({  
        "errors": [
            {
                "code": "500",
                "message": "INTERNAL SERVER ERROR",
                "level": "error",
                "description": str(e)
            }
    ]}), 500

def no_registrado(padron):
    return jsonify({
        "errors": [
            {
                    "code": "404",
                    "message": "NOT FOUND",
                    "level": "error",
                    "description": f"No se encontró registrado un usuario con el padrón {padron}."
            }
        ]
    }), 404

def contrasena_incorrecta():
    return jsonify({
        "errors": [
            {
                    "code": "401",
                    "message": "UNAUTHORIZED",
                    "level": "error",
                    "description": f"Contraseña incorrecta"
            }
        ]
    }), 401

def datos_incompletos():
    return jsonify({
        "errors": [
            {
                    "code": "400",
                    "message": "BAD REQUEST",
                    "level": "error",
                    "description": f"Falta ingresar datos requeridos"
            }
        ]
    }), 400

def datos_incorrectos(dato):
    return jsonify({
        "errors": [
            {
                    "code": "400",
                    "message": "BAD REQUEST",
                    "level": "error",
                    "description": f"Se han introducido datos incorrectos: {dato} "
            }
        ]
    }), 400


def ya_existe():
    return jsonify({
        'errors': [
            {
                "code":"409",
                "message":"CONFLICT",
                "level":"error",
                "description":f"Ya existe un usuario con ese padrón"
                }
            ]
        }), 409


def acceso_denegado():
    return jsonify({
        "errors": [
            {
                "code":"401",
                "message": "UNAUTHORIZED",
                "level": "error",
                "description": f"Acesso denegado"
            }
        ]
    }), 401

def error_enviando_correo(e):
    return jsonify({
        "errors": [
            {
                    "code": "500",
                    "message": "SERVER ERROR",
                    "level": "error",
                    "description": str(e)
            }
        ]
    }), 401


def not_found(error):
        error404 ={
                "error": [
                    {
                        "code": 404,
                        "message": "No encontrado",
                        "level": "info",
                        "description": str(error)
                    }
                ]
            }
        return error404

def bad_request(error):
    error400 = {"error": [
            {
                "code": 400,
                "message": "Petición inválida",
                "level": "info",
                "description": error
            }
        ]
    }
    return error400

def conflict_error(error):
    error409 = {
        "error": [
            {
                "code": 409,
                "message": "Conflicto",
                "level": "warning",
                "description": str(error)
            }
        ]
    }
    return error409
