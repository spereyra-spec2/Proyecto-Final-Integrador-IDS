def error_response(code, message, level="error", description=""):
    return {
        "error": [{
            "code": code,
            "message": message,
            "level": level,
            "description": description
        }]
    }, code

def not_found(resource="recurso"):
    return error_response(404, f"{resource} no encontrado", "info", f"No se encontró el {resource} solicitado.")

def bad_request(detail="Petición inválida"):
    return error_response(400, "Petición inválida", "warning", detail)

def server_error(detail="Error interno del servidor"):
    return error_response(500, "Error interno", "critical", detail)

def conflict(detail="Conflicto"):
    return error_response(409, "Conflicto", "warning", detail)