from flask import jsonify

def server_error():
    return jsonify({  
        "errors": [
            {
                "code": "500",
                "message": "INTERNAL SERVER ERROR",
                "level": "error",
                "description": "Hubo un error al conectarse con la base de datos."
            }
    ]}), 500

def no_registrado(padron):
    return jsonify({
        "errors": [
            {
                    "code": "404",
                    "message": "NOT FOUND",
                    "level": "error",
                    "description": f"No se encontró un usuario con el padrón {padron}."
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