from flask import jsonify, Request, Response, url_for
from typing import Any
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

FIELDS: set = {"padron", "curso_ID", "grupo_ID", "nombres", "mail", "cursando_actualmente"}
MAX_LIMIT: int = 50

def validar_entero(param: Any, nombre: str, valor_min: int | float = float('-inf'), valor_max: int | float = float('inf')) -> dict[str, int | str] | None:
    if param is not None:
        try:
            param_int = int(param)
            if param_int < valor_min or param_int > valor_max:
                return bad_request(f"El parámetro \"{nombre}\" está fuera del rango permitido: {valor_min} – {valor_max}.")
        except (TypeError, ValueError):
            return bad_request(f"El parámetro \"{nombre}\" debe ser un número entero.")

def validar_booleano(param: Any, nombre: str) -> dict[str, int | str] | None:
    if param is not None:
        try:
            param_lower: str = str(param).lower()

            if not param_lower in ['0', "false", '1', "true"]:
                return bad_request(f"El parámetro \"{nombre}\" debe ser un valor booleano (0/false/1/true).")
        except (TypeError, ValueError):
            return bad_request(f"El parámetro \"{nombre}\" debe ser un valor booleano (0/false/1/true).")

def validar_fields(fields: Any) -> dict[str, int | str] | None:
    if fields is not None:
        try:
            fields_set: set = set(str(fields).split(','))
            if not fields_set.issubset(FIELDS):
                return bad_request(f"El parámetro \"fields\" contiene campos no válidos. Campos válidos: {', '.join(FIELDS)}.")
        except (TypeError, ValueError):
            return bad_request(f"El parámetro \"fields\" debe ser una lista de campos separados por comas. Campos válidos: {', '.join(FIELDS)}.")

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

def validaciones_get_alumnos(
        offset: Any,
        limit: Any,
        grupo_id: Any,
        padron_min: Any,
        padron_max: Any,
        cursando: Any,
        fields: Any
) -> dict[str, int | str] | None:
    errores: list[dict[str, int | str]] = []

    errores.append(validar_entero(offset, "offset", 0))
    errores.append(validar_entero(limit, "limit", 1, MAX_LIMIT))
    errores.append(validar_entero(grupo_id, "grupo_id", 0))
    errores.append(validar_entero(padron_min, "padron_min", 0, 999999))
    errores.append(validar_entero(padron_max, "padron_max", 0, 999999))
    errores.append(validar_booleano(cursando, "cursando"))
    errores.append(validar_fields(fields))

    errores = [error for error in errores if error is not None]
    return errores if errores else None

def validar_cuerpo_json(request: Request):
    try:
        datos: Any = request.get_json()
    except UnsupportedMediaType:
        return None, unsupported_media_type("El Content-Type de la solicitud debe ser application/json.")
    except BadRequest:
        return None, bad_request("El cuerpo de la solicitud debe ser un JSON válido.")

    if not datos or datos is None or (isinstance(datos, dict) and len(datos) == 0):
        return None, bad_request("El cuerpo de la solicitud no puede estar vacío.")

    if not all(v is not None and str(v).strip() != "" for v in list(datos.values())):
        return None, bad_request("Los campos no pueden ser nulos o vacíos.")
    
    return datos, None

#------------------------

def construir_query_get(args: dict[str, Any], count: bool = False) -> tuple[str, list[int | bool]]:

    if not count:
        query: str = f"""
            SELECT {args.get("fields", ','.join(FIELDS)).replace(',', ", ")}
            FROM usuarios
            WHERE rol = "estudiantes"
        """
    else:
        query = """
            SELECT COUNT(*) AS total
            FROM usuarios
            WHERE rol = "estudiantes"
        """

    params: list[int | bool] = []

    if "curso_id" in args:
        query += " AND curso_ID = %s"
        params.append(int(args["curso_id"]))

    if "grupo_id" in args:
        query += " AND grupo_ID = %s"
        params.append(int(args["grupo_id"]))

    if "padron_min" in args:
        query += " AND padron >= %s"
        params.append(int(args["padron_min"]))

    if "padron_max" in args:
        query += " AND padron <= %s"
        params.append(int(args["padron_max"]))

    if "cursando" in args:
        query += " AND cursando_actualmente = %s"
        params.append(0) if str(args["cursando"]).lower() in ['0', "false"] else params.append(1)

    if not count:
        query += " ORDER BY padron ASC LIMIT %s OFFSET %s"
        params.extend([int(args.get("limit", 50)), int(args.get("offset", 0))])

    return query, params

#------------------------

def hateoas_response(datos: list[dict[str, Any]], curso_id: int, params: dict[str, Any], offset: int, limit: int, total: int) -> Response:
    return jsonify({
        "alumnos": datos,
        "links": {
            "first": {
                "href": url_for('alumnos.get_alumnos', curso_id=curso_id, **params, offset = 0, limit = limit, _external=True)
            },
            "prev": {
                "href": url_for('alumnos.get_alumnos',
                                curso_id=curso_id,
                                **params,
                                offset = offset - limit if offset - limit >= 0 else (total - 1) // limit * limit if total > 0 else 0,
                                limit = limit,
                                _external=True)
            },
            "next": {
                "href": url_for('alumnos.get_alumnos',
                                curso_id=curso_id,
                                **params,
                                offset = limit + offset if limit + offset < total else 0,
                                limit = limit, _external=True)
            },
            "last": {
                "href": url_for('alumnos.get_alumnos', curso_id=curso_id, **params, offset = max(total - limit, 0), limit = limit, _external=True)
            }
        }
    }), 200

def ok_response(datos: dict[str, Any]) -> Response:
    return jsonify(datos), 200

def error_response(code, message, level="error", description=""):
    return {
        "code": code,
        "message": message,
        "level": level,
        "description": description
    }


def not_found(detail):
    return error_response(404, "No encontrado", "warning", detail)

def conflict(detail):
    return error_response(409, "Conflicto", "error", detail)

def server_error(detail="Error interno del servidor"):
    return error_response(500, "Error interno del servidor", "critical", detail)

def bad_request(detail):
    return error_response(400, "Petición inválida", "error", detail)

def unsupported_media_type(detail):
    return error_response(415, "Formato del cuerpo no soportado", "error", detail)

def unauthorized(detail):
    return error_response(401, "No autorizado", "error", detail)

def forbidden(detail):
    return error_response(403, "Prohibido", "error", detail)

def unprocessable_entity(detail):
    return error_response(422, "Entidad no procesable", "error", detail)