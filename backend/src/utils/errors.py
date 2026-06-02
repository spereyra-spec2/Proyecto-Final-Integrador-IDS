from flask import jsonify

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


def ya_existe_alumno():
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

def server_error(error):
    error500 = {"error": [
                    {
                        "code": 500,
                        "message": "Error interno en el servidor",
                        "level": "error",
                        "description": str(error)
                    }
                ]
            }
    return error500

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
