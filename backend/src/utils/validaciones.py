# validaciones.py
import re
from flask import Request
from typing import Any
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from src.utils.errors import bad_request, conflict, unsupported_media_type

FIELDS: set = {"padron", "curso_ID", "grupo_ID", "nombres", "mail", "cursando_actualmente"}
MAX_LIMIT: int = 50

#------------------------------------------------------------------------------------------------
def validar_email_fiuba(email):
    usuario = ""
    dominio = ""

    if email and '@' in email:
        partes = email.rsplit('@', 1)
        usuario = partes[0].strip()
        dominio = partes[1].strip()
        
    return usuario != '' and dominio == 'fi.uba.ar'

#--------------------------------------------------------------------------------------------------------

def validar_entero(param: Any, nombre: str, valor_min: int | float = float('-inf'), valor_max: int | float = float('inf')) -> dict[str, int | str] | None:
    if param is not None:
        try:
            param_int = int(param)
            if param_int < valor_min or param_int > valor_max:
                return bad_request(f"El parámetro \"{nombre}\" está fuera del rango permitido: {valor_min} – {valor_max}.")
        except (TypeError, ValueError):
            return bad_request(f"El parámetro \"{nombre}\" debe ser un número entero.")
    return None

#--------------------------------------------------------------------------------------------------------------------  

def validar_booleano(param: Any, nombre: str) -> dict[str, int | str] | None:
    if param is not None:
        try:
            param_lower: str = str(param).lower()
            if not param_lower in ['0', "false", '1', "true"]:
                return bad_request(f"El parámetro \"{nombre}\" debe ser un valor booleano (0/false/1/true).")
        except (TypeError, ValueError):
            return bad_request(f"El parámetro \"{nombre}\" debe ser un valor booleano (0/false/1/true).")
    return None

#------------------------------------------------------------------------------------------------------

def validar_fields(fields: Any) -> dict[str, int | str] | None:
    if fields is not None:
        try:
            fields_set: set = set(str(fields).split(','))
            if not fields_set.issubset(FIELDS):
                return bad_request(f"El parámetro \"fields\" contiene campos no válidos. Campos válidos: {', '.join(FIELDS)}.")
        except (TypeError, ValueError):
            return bad_request(f"El parámetro \"fields\" debe ser una lista de campos separados por comas. Campos válidos: {', '.join(FIELDS)}.")
    return None

#------------------------------------------------------------------------------------------------------------

def validaciones_get_alumnos(offset: Any, limit: Any, grupo_id: Any, padron_min: Any, padron_max: Any, cursando: Any, fields: Any) -> list[dict[str, int | str]] | None:
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

#------------------------------------------------------------------------------------------------------

def validar_cuerpo_json(request: Request) -> tuple[Any, dict[str, int | str] | None]:
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

#-------------------------------------------------------------------------------------------------------------

def es_email_valido(mail):
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(patron, mail):
        return True
    return False

#--------------------------------------------------------------------------------------------------------------
def validar_curso_datos(nombre: Any, codigo: Any) -> dict[str, int | str] | None:

    if not nombre or str(nombre).strip() == "":
        return bad_request("El nombre del curso es obligatorio.")
    
    if len(str(nombre).strip()) < 1:
        return bad_request("El nombre del curso debe tener al menos 1 letra.")
        
    if not codigo or str(codigo).strip() == "":
        return bad_request("El código del curso es obligatorio.")
        
    return None

#--------------------------------------------------------------------------------------------------------------

def verificar_unicidad_curso(cursor, nombre: str, codigo: str, id_curso_ignorar: int = None) -> dict[str, int | str] | None:

    query = "SELECT nombre, codigo FROM Curso WHERE (nombre = %s OR codigo = %s)"
    params = [nombre, codigo]
    
    if id_curso_ignorar is not None:
        query += " AND idCurso != %s"
        params.append(id_curso_ignorar)
        
    cursor.execute(query, tuple(params))
    existente = cursor.fetchone()
    
    if existente:
        if existente["nombre"].lower() == nombre.lower():
            return conflict("Ya existe un curso registrado con ese mismo nombre.")
        if existente["codigo"].lower() == codigo.lower():
            return conflict("Ya existe un curso registrado con ese mismo código.")
            
    return None