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
