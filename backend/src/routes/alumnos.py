import io
import csv
from src.utils.seguridad import verify_token
from db import get_connection
from flask import request, Response, jsonify, Blueprint
from typing import Any
import mysql.connector
from mysql.connector import IntegrityError

import src.utils.funciones as funciones

alumnos_bp = Blueprint('alumnos', __name__)

DEFAULT_OFFSET: int = 0
DEFAULT_LIMIT: int = 50

#-------------------------

@alumnos_bp.route('', methods=["GET"])
def get_alumnos(curso_id: int) -> Response:
    """
    Lista los alumnos registrados con paginación mediante los query params "offset" y "limit".

    Permite filtrar por un grupo específico mediante el query param "grupo_id".

    Permite filtrar por un rango de padrones mediante los query params "padron_min" y "padron_max".

    Permite filtrar por alumnos que estén o no cursando actualmente con el query param "cursando" (0/false/1/true).

    Permite elegir los campos a mostrar mediante el query param "fields" (FIELDS, separados por comas):
    Si no se especifica "fields", se muestran todos los campos por defecto.
    """

    offset: Any = request.args.get("offset", DEFAULT_OFFSET)
    limit: Any = request.args.get("limit", DEFAULT_LIMIT)
    grupo_id: Any = request.args.get("grupo_id")
    padron_min: Any = request.args.get("padron_min")
    padron_max: Any = request.args.get("padron_max")
    cursando: Any = request.args.get("cursando")
    fields: Any = request.args.get("fields")

    errores: list[dict[str, int | str]] = funciones.validaciones_get_alumnos(
        offset,
        limit,
        grupo_id,
        padron_min,
        padron_max,
        cursando,
        fields)

    if errores:
        return jsonify({"errors": errores}), 400
    
    try:
        query, params = funciones.construir_query_get(request.args.to_dict())
        
        query_count, params_count = funciones.construir_query_get(request.args.to_dict(), count = True)

        with get_connection() as conexion:
            with conexion.cursor(buffered = True, dictionary = True) as cursor:
                cursor.execute(query, params)
                alumnos: list[dict[str, Any]] = cursor.fetchall()
                cursor.execute(query_count, params_count)
                total = cursor.fetchone().get("total", 0)
            conexion.commit()

    except mysql.connector.Error as e:
        return jsonify({
            "errors": [
                funciones.server_error(str(e))
            ]
        }), 500
    
    if alumnos:
        return funciones.hateoas_response(alumnos, curso_id, {k: v for k, v in request.args.to_dict().items() if k != "offset" and k != "limit"}, int(offset), int(limit), total)

    return jsonify({
        "errors": [
            funciones.not_found("No se encontraron alumnos que coincidan con los criterios de búsqueda.")
        ]
    }), 404

#-------------------------

@alumnos_bp.route("/<int:padron>", methods=["GET"])
def get_alumno(curso_id: int, padron: int) -> Response:
    with get_connection() as conexion:
        with conexion.cursor(buffered = True, dictionary = True) as cursor:
            cursor.execute("""SELECT
                                padron, nombres, mail, rol, curso_ID, grupo_ID, cursando_actualmente, fecha_creacion
                            FROM usuarios
                            WHERE padron = %s AND rol = 'estudiantes'""", (padron,))
            alumno = cursor.fetchone()
        conexion.commit()

    if alumno:
        return funciones.ok_response(alumno)
    else:
        return jsonify({
            "errors": [
                funciones.not_found("Alumno no encontrado.")
            ]
        }), 404

#-------------------------

@alumnos_bp.route("/<int:padron>", methods=["PUT"])
def update_alumno(curso_id: int, padron: int):
    """
    No deja actualizar contrasena_hash ni fecha_creacion. La contraseña se modifica en el PUT. La fecha de creación nunca se puede cambiar.

    Busca el padrón dentro del token y verifica si coincide con el padrón del path param, o si el rol del padrón asociado es de profesor.
    En el primer caso, no se permiten modificar rol, curso_ID, grupo_ID ni cursando_actualmente; en el segundo caso sí.
    """
    
    # Uso la misma lógica que la rama de Julieta
    payload, error = verify_token(request)

    if error:
        return jsonify(error), 401

    usuario_padron = payload["padron"]
    usuario_rol = payload["rol"]

    if usuario_padron != padron and usuario_rol != "docente":
        return funciones.forbidden("No se tienen los permisos necesarios para modificar los datos de este alumno."), 403

    datos, error = funciones.validar_cuerpo_json(request)
    
    if error:
        return jsonify({
            "errors": [
                error
            ]
        }), 400

    campos: set = {"nombres", "mail"}
    campos_permiso: set = {"rol", "curso_ID", "grupo_ID", "cursando_actualmente"}
    errores: list = []

    if not all(campo in campos.union(campos_permiso) for campo in datos.keys()):
        errores.append(funciones.bad_request(f"La solicitud debe contener los siguientes campos: {', '.join(campos)}"))
    
    if any(campo in campos_permiso for campo in datos.keys()) and usuario_rol != "docente":
        errores.append(funciones.forbidden(f"No se tienen los permisos necesarios para modificar ninguno de estos campos: {', '.join(campo for campo in datos.keys() if campo in campos_permiso)}"))

    if not all(isinstance(datos[campo], str) for campo in campos.union({"rol"}).intersection(datos.keys())):
        errores.append(funciones.unprocessable_entity("Los campos 'nombres', 'mail' y 'rol' deben ser de tipo string."))

    if "rol" in datos and datos["rol"] not in {"estudiantes", "docente"}:
        errores.append(funciones.unprocessable_entity("El campo 'rol' solo puede tomar los valores 'estudiantes' o 'docente'."))

    if not all(isinstance(datos[campo], int) for campo in {"curso_ID", "grupo_ID", "cursando_actualmente"}.intersection(datos.keys())):
        errores.append(funciones.unprocessable_entity("Los campos 'curso_ID' y 'grupo_ID' deben ser de tipo entero."))

    if not funciones.validar_email_fiuba(datos.get("mail")):
        errores.append(funciones.unprocessable_entity("El formato del correo es inválido. Debe pertenecer al dominio 'fi.uba.ar'"))
    
    errores.append(funciones.validar_booleano(datos.get("cursando_actualmente"), "cursando_actualmente"))
    errores = [error for error in errores if error is not None]

    if errores:
        return jsonify({"errors": errores}), 422
    
    try:
        with get_connection() as conexion:
            with conexion.cursor(buffered = True, dictionary = True) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE padron = %s AND rol = 'estudiantes'", (padron,))
                alumno = cursor.fetchone()

                if not alumno:
                    return jsonify({
                        "errors": [
                            funciones.not_found("Alumno no encontrado.")
                        ]
                    }), 404

                query = "UPDATE usuarios SET "+ ", ".join(f"{campo} = %s" for campo in datos.keys())
                query += " WHERE padron = %s AND rol = 'estudiantes'"
                params = list(datos.values()) + [padron]
                cursor.execute(query, params)
            conexion.commit()
        
        datos.setdefault("curso_ID", alumno["curso_ID"])
        datos.setdefault("grupo_ID", alumno["grupo_ID"])
        datos.setdefault("cursando_actualmente", alumno["cursando_actualmente"])
        datos.setdefault("rol", alumno["rol"])
        datos.setdefault("fecha_creacion", alumno["fecha_creacion"])

        return jsonify({
            "padron": padron,
            **datos
        }), 200
    except mysql.connector.Error as e:
        return jsonify({
            "errors": [
                funciones.server_error(str(e))
            ]
        }), 500

#-------------------------

@alumnos_bp.route("/<int:padron>", methods=["PATCH"])
def patch_alumno(curso_id: int, padron: int):
    """
    Deja modificar un solo campo, incluyendo contrasena_hash, pero no fecha_creacion.

    El padrón del token tiene que coincidir con el padrón del path param.
    En caso de que se intente cambiar rol, grupo_ID, curso_ID o cursando_actualmente, solo se permite si el rol del usuario asociado al token es docente.
    """

    payload, error = verify_token(request)

    if error:
        return jsonify(error), 401

    usuario_padron = payload["padron"]
    usuario_rol = payload["rol"]

    if usuario_padron != padron and usuario_rol != "docente":
        return funciones.forbidden("No se tienen los permisos necesarios para modificar los datos de este alumno."), 403

    datos, error = funciones.validar_cuerpo_json(request)
    
    if error:
        return jsonify({
            "errors": [
                error
            ]
        }), 400

    if len(datos) != 1:
        return jsonify({
            "errors": [
                funciones.bad_request("La solicitud debe contener exactamente un campo a modificar.")
            ]
        }), 400
    
    campos: set = {"nombres", "mail", "contrasena_hash"}
    campos_permiso: set = {"rol", "curso_ID", "grupo_ID", "cursando_actualmente"}
    errores: list[dict[str, int | str]] = []

    if list(datos.keys())[0] not in campos.union(campos_permiso):
        errores.append(funciones.bad_request(f"El campo a modificar debe ser uno de los siguientes: {', '.join(campos.union(campos_permiso))}"))

    if list(datos.keys())[0] in campos_permiso and usuario_rol != "docente":
        errores.append(funciones.forbidden(f"No se tienen los permisos necesarios para modificar el campo '{list(datos.keys())[0]}'"))

    if list(datos.keys())[0] in campos.union({"rol"}) and not isinstance(list(datos.values())[0], str):
        errores.append(funciones.unprocessable_entity(f"El campo '{list(datos.keys())[0]}' debe ser de tipo string."))
    
    if list(datos.keys())[0] in {"curso_ID", "grupo_ID", "cursando_actualmente"} and not isinstance(list(datos.values())[0], int):
        errores.append(funciones.unprocessable_entity(f"El campo '{list(datos.keys())[0]}' debe ser de tipo entero."))
    
    if list(datos.keys())[0] == "rol" and list(datos.values())[0] not in {"estudiantes", "docente"}:
        errores.append(funciones.unprocessable_entity("El campo 'rol' solo puede tomar los valores 'estudiantes' o 'docente'."))

    if list(datos.keys())[0] == "mail" and not funciones.validar_email_fiuba(list(datos.values())[0]):
        errores.append(funciones.unprocessable_entity("El formato del correo es inválido. Debe pertenecer al dominio 'fi.uba.ar'"))

    if list(datos.keys())[0] == "contrasena_hash" and padron != usuario_padron:
        errores.append(funciones.forbidden("No se tienen los permisos necesarios para modificar la contraseña de este alumno."))
    
    errores.append(funciones.validar_booleano(list(datos.values())[0], list(datos.keys())[0]) if list(datos.keys())[0] == "cursando_actualmente" else None)

    errores = [error for error in errores if error is not None]
    
    if errores:
        return jsonify({"errors": errores}), 400

    try:
        with get_connection() as conexion:
            with conexion.cursor(buffered = True, dictionary = True) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE padron = %s AND rol = 'estudiantes'", (padron,))
                alumno = cursor.fetchone()

                if not alumno:
                    return jsonify({
                        "errors": [
                            funciones.not_found("Alumno no encontrado.")
                        ]
                    }), 404

                query = f"UPDATE usuarios SET {list(datos.keys())[0]} = %s WHERE padron = %s AND rol = 'estudiantes'"
                params = [list(datos.values())[0], padron]
                cursor.execute(query, params)
            conexion.commit()

        datos.setdefault("nombres", alumno["nombres"])
        datos.setdefault("mail", alumno["mail"])
        datos.setdefault("rol", alumno["rol"])
        datos.setdefault("curso_ID", alumno["curso_ID"])
        datos.setdefault("grupo_ID", alumno["grupo_ID"])
        datos.setdefault("cursando_actualmente", alumno["cursando_actualmente"])
        datos.setdefault("rol", alumno["rol"])
        datos.setdefault("fecha_creacion", alumno["fecha_creacion"])

        return jsonify({
            "padron": padron,
            **datos
        }), 200
    except mysql.connector.Error as e:
        return jsonify({
            "errors": [
                funciones.server_error(str(e))
            ]
        }), 500
#-------------------------

@alumnos_bp.route('', methods=['POST']) 
def add_alumno(curso_id):
    conn = None
    cursor = None
    
    try:
        data = request.get_json(silent=True)

        # Validación de campos obligatorios 
        campos_requeridos = ["padron", "nombres", "mail"]
        faltantes = [
            campo for campo in campos_requeridos 
            if campo not in data or str(data.get(campo)).strip() == ""
        ]
        if faltantes:
            return funciones.bad_request(f"Faltan campos obligatorios: {', '.join(faltantes)}")

        
        nombres = str(data["nombres"]).strip()
        mail = str(data["mail"]).strip()
        padron = int(data["padron"])
        rol = "estudiantes" 

        # Validación mail fiuba
        if not funciones.validar_email_fiuba(mail):
            return funciones.bad_request("El formato del correo es inválido. Debe pertenecer al dominio 'fi.uba.ar'")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            INSERT INTO usuarios (padron, nombres, mail, rol) 
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(query, (padron, nombres, mail, rol))
        
        conn.commit()
        return jsonify({"mensage": "Alumno registrado correctamente"}), 201

    except IntegrityError:
        if conn:
            conn.rollback()
        return funciones.conflict("El padrón o correo electrónico ya se encuentra registrado")
    except Exception as e:
        if conn:
            conn.rollback()
        return funciones.server_error(str(e))
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------------------------

@alumnos_bp.route('/importar', methods=['POST'])
def importar_alumnos(curso_id):
    conn = None
    cursor = None   
    try:
        # Verificar si el archivo viene en la request
        if 'file' not in request.files:
            return funciones.bad_request("No se encontró ningún archivo en la solicitud. Asegúrese de enviar el archivo con el campo 'file'.")
            
        file = request.files['file']
        
        #Verificar que el archivo tenga un nombre válido 
        if file.filename == '':
            return funciones.bad_request("No se seleccionó ningún archivo para subir.")
        
        # Verificar extensión del archivo
        if not file.filename.endswith('.csv'):
            return funciones.bad_request("El archivo debe tener extensión .csv")

       
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream) 
        
        alumnos_a_insertar = []
        campos_esperados = ["padron", "nombres", "mail"]

        # Validar consistencia de datos fila por fila
        for row in csv_input:
           
            row = {k.strip(): v.strip() for k, v in row.items()}
            
            if not all(campo in row for campo in campos_esperados):
                return funciones.bad_request("El archivo CSV debe contener las columnas: padron, nombres, mail")
            
            alumnos_a_insertar.append((
                row["padron"], 
                row["nombres"], 
                row["mail"], 
                "estudiantes" 
            ))

        if not alumnos_a_insertar:
            return funciones.bad_request("El archivo CSV está vacío o no contiene registros válidos.")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO usuarios (padron, nombres, mail, rol) 
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.executemany(query, alumnos_a_insertar)
        conn.commit()
        registros_insertados = cursor.rowcount

        return jsonify({
            "message": "Archivo procesado con éxito", 
            "registros_insertados": registros_insertados
        }), 201

    except IntegrityError:
        return funciones.conflict("Uno o más registros en el CSV ya existen (Padrón o Email duplicado).")
    except Exception as e:
        return funciones.server_error(str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
#-------------------------

@alumnos_bp.route('/<int:padron>', methods=['DELETE'])
def delete_alumno(curso_id, padron):
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si el alumno existe 
        query_verificar = """
            SELECT cursando_actualmente 
            FROM usuarios 
            WHERE padron = %s 
        """
        cursor.execute(query_verificar, (padron,))
        alumno = cursor.fetchone()
        
        if not alumno:
            return funciones.not_found(f"No se encontró ningún alumno con el padrón {padron}")
            
        # Verificar si ya se encontraba dado de baja 
        if not alumno['cursando_actualmente']:
            return funciones.bad_request(f"El alumno con padrón {padron} ya se encuentra dado de baja")

        
        query_baja = """
            UPDATE usuarios 
            SET cursando_actualmente = FALSE
            WHERE padron = %s
        """
    
        cursor.execute(query_baja, (padron,))
        conn.commit()
        
        return jsonify({
            "message": f"Alumno con padrón {padron} desactivado correctamente del sistema"
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return funciones.server_error(str(e))
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
