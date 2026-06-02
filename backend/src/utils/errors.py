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
