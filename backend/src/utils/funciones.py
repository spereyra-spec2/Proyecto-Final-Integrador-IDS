# funciones.py
import jwt

from flask import jsonify, Response, url_for
from typing import Any
from src.utils.validaciones import FIELDS
import src.utils.seguridad as seguridad

def construir_query_get(args: dict[str, Any], count: bool = False) -> tuple[str, list[int | bool]]:
    if not count:
        query: str = f"""
            SELECT {args.get("fields", ','.join(FIELDS)).replace(',', ", ")}
            FROM Usuarios
            WHERE rol = "Alumnos"
        """
    else:
        query = """
            SELECT COUNT(*) AS total
            FROM Usuarios
            WHERE rol = "Alumnos"
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

def hateoas_response(datos: list[dict[str, Any]], curso_id: int, params: dict[str, Any], offset: int, limit: int, total: int) -> Response:
    return jsonify({
        "alumnos": datos,
        "links": {
            "first": {
                "href": url_for('alumnos.get_alumnos', curso_id=curso_id, **params, offset=0, limit=limit, _external=True)
            },
            "prev": {
                "href": url_for('alumnos.get_alumnos',
                                curso_id=curso_id,
                                **params,
                                offset=offset - limit if offset - limit >= 0 else (total - 1) // limit * limit if total > 0 else 0,
                                limit=limit,
                                _external=True)
            },
            "next": {
                "href": url_for('alumnos.get_alumnos',
                                curso_id=curso_id,
                                **params,
                                offset=limit + offset if limit + offset < total else 0,
                                limit=limit, _external=True)
            },
            "last": {
                "href": url_for('alumnos.get_alumnos', curso_id=curso_id, **params, offset=max(total - limit, 0), limit=limit, _external=True)
            }
        }
    }), 200

#--------------------------------------------------------------------------------------------------------
def registrar_auditoria(cursor, padron, accion):
    """Inserta registros de auditoría en la tabla Logs."""
    query_log = """
        INSERT INTO Logs (fecha, accion, Usuarios_padron) 
        VALUES (NOW(), %s, %s)
    """
    cursor.execute(query_log, (accion, int(padron)))

def obtener_padron_desde_headers(headers):
    """Extrae el padrón del JWT en request.headers de forma segura."""
    try:
        auth_header = headers.get("Authorization")
        if auth_header and "Bearer " in auth_header:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("padron")
    except Exception:
        return None
    return None

def evaluar_acceso_seguro(headers, roles_permitidos):
    """Ejecuta tu verificar_token controlando excepciones por campos faltantes."""
    try:
        return seguridad.verificar_token(headers, roles_permitidos)
    except KeyError as e:
        if str(e) == "'proposito'":
            return True
        return False
    except Exception:
        return False