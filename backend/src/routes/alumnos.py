# alumnos.py
import io
import csv
import jwt  
from src.db.db import _get_connection
from flask import request, Blueprint
from mysql.connector import IntegrityError
from src.utils.errors import (
    not_found, conflict, server_error, bad_request, ok_response, created_response, acceso_denegado1, )
import src.utils.validaciones as validaciones
import src.utils.funciones as funciones

alumnos_bp = Blueprint('alumnos', __name__)

DEFAULT_OFFSET: int = 0
DEFAULT_LIMIT: int = 50

#--------------------------------------------------------------------------------------------------------
# POST / api/ cursos/{curso-id}/alumnos 
# Agrega un alumno a un curso específico. 
#--------------------------------------------------------------------------------------------------------
@alumnos_bp.route('', methods=['POST']) 
def add_alumno(idCurso):
    
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return acceso_denegado1("No tiene permisos para agregar alumnos o token inválido")
    
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    if not padron_operador:
        return bad_request("No se pudo identificar el padrón del operador en el token.")
    
    conn = None
    cursor = None
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return bad_request("No se recibió un cuerpo JSON válido en la solicitud.")

        campos_requeridos = ["padron", "nombres", "mail"]
        faltantes = [
            campo for campo in campos_requeridos 
            if campo not in data or str(data.get(campo)).strip() == ""
        ]
        if faltantes:
            return bad_request(f"Faltan campos obligatorios: {', '.join(faltantes)}")

        nombres = str(data["nombres"]).strip()
        mail = str(data["mail"]).strip()
        padron = int(data["padron"])
        rol = "Alumno" 

        if not validaciones.validar_email_fiuba(mail):
            return bad_request("El formato del correo es inválido. Debe pertenecer al dominio 'fi.uba.ar'")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_usuario = """
            INSERT INTO Usuarios (padron, rol, nombres, mail, cursando_actualmente, created_at) 
            VALUES (%s, %s, %s, %s, 1, NOW())
        """
        cursor.execute(query_usuario, (padron, rol, nombres, mail))

        query_relacion = """
            INSERT IGNORE INTO Curso_has_Usuarios (Curso_idCurso, Usuarios_padron, Estado)
            VALUES (%s, %s, 1)
        """
        cursor.execute(query_relacion, (idCurso, padron))

        funciones.registrar_auditoria(cursor, padron_operador, f"Agregó manualmente al alumno {padron} al curso {idCurso}")

        conn.commit()
        return created_response(f"Alumno con padrón {padron} agregado correctamente al curso {idCurso}")
    
    except IntegrityError:
        if conn: conn.rollback()
        return conflict("El padrón o correo electrónico ya se encuentra registrado")
    except Exception as e:
        if conn: conn.rollback()
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# POST / api/ cursos/ {curso-id}/ alumnos/ importar 
# Procesa el archivo CSV e inscribe masivamente a los alumnos en el curso indicado en la URL.
#--------------------------------------------------------------------------------------------------------

@alumnos_bp.route('/importar', methods=['POST'])
def importar_alumnos(idCurso):
    
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return acceso_denegado1("No tiene permisos para agregar alumnos o token inválido")
    
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    if not padron_operador:
        return bad_request("No se pudo identificar el padrón del operador en el token.")
    
    conn = None
    cursor = None   

    try:
        if 'file' not in request.files:
            return bad_request("No se encontró ningún archivo en la solicitud.")
            
        file = request.files['file']
        
        if file.filename == '':
            return bad_request("No se seleccionó ningún archivo para subir.")
        
        if not file.filename.endswith('.csv'):
            return bad_request("El archivo debe tener extensión .csv")

        conn = _get_connection()
        cursor = conn.cursor()
        
        query_existentes = "SELECT Usuarios_padron FROM Curso_has_Usuarios WHERE Curso_idCurso = %s"
        cursor.execute(query_existentes, (idCurso,))
        

        padrones_ya_inscriptos = set(row[0] for row in cursor.fetchall())

        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream) 
        
        alumnos_a_insertar = []
        padrones_vistos_csv = set() 
        campos_esperados = ["padron", "nombres", "mail"]

        for row in csv_input:
            row = {k.strip(): v.strip() for k, v in row.items()}
            
            if not all(campo in row for campo in campos_esperados):
                return bad_request("El archivo CSV debe contener las columnas: padron, nombres, mail")
            
            try:
                padron_actual = int(row["padron"])
            except ValueError:
                return bad_request(f"El padrón '{row['padron']}' no es un número válido.")

            if padron_actual in padrones_vistos_csv:
                continue
            padrones_vistos_csv.add(padron_actual)

            if padron_actual in padrones_ya_inscriptos:
                continue 

            if not validaciones.validar_email_fiuba(row["mail"]):
                return bad_request(f"El correo '{row['mail']}' es inválido. Debe ser @fi.uba.ar")

            alumnos_a_insertar.append((
                padron_actual, 
                "Alumno",
                row["nombres"], 
                row["mail"]
            ))

        if not alumnos_a_insertar:
            return ok_response("Todos los alumnos del archivo ya se encuentran registrados en este curso. No se agregaron nuevos registros.")
        
        query_usuario = """
            INSERT INTO Usuarios (padron, rol, nombres, mail, cursando_actualmente, created_at) 
            VALUES (%s, %s, %s, %s, 1, NOW())
            ON DUPLICATE KEY UPDATE cursando_actualmente = 1
        """
        cursor.executemany(query_usuario, alumnos_a_insertar)

        relaciones = [(idCurso, alumno[0]) for alumno in alumnos_a_insertar]    

        query_relacion = """
            INSERT IGNORE INTO Curso_has_Usuarios (Curso_idCurso, Usuarios_padron, Estado)
            VALUES (%s, %s, 1)
        """
        cursor.executemany(query_relacion, relaciones)

        funciones.registrar_auditoria(
            cursor, 
            padron_operador, 
            f"Importó masivamente {len(alumnos_a_insertar)} nuevos alumnos netos al curso {idCurso}"
        )

        conn.commit()
        return created_response(f"Importación finalizada con éxito. Se añadieron {len(alumnos_a_insertar)} alumnos nuevos a la comisión.")
    
    except Exception as e:
        if conn: conn.rollback()
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
#--------------------------------------------------------------------------------------------------------
# DELETE / api/ cursos/ {curso-id}/ alumnos/{padrón}
# Baja lógica del alumno solo en ese curso.
#--------------------------------------------------------------------------------------------------------
@alumnos_bp.route('/<int:padron>', methods=['DELETE'])
def delete_alumno(idCurso, padron):
    
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return acceso_denegado1("No autorizado o token inválido")
    
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    if not padron_operador:
        return bad_request("No se pudo identificar el padrón del operador en el token.")

    conn = None
    cursor = None
    
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_verificar = """
            SELECT Estado 
            FROM Curso_has_Usuarios 
            WHERE Curso_idCurso = %s AND Usuarios_padron = %s
        """
        cursor.execute(query_verificar, (idCurso, padron))
        inscripcion = cursor.fetchone()
        
        if not inscripcion:
            return not_found(f"El alumno con padrón {padron} no está inscrito en el curso {idCurso}")
            
        if inscripcion['Estado'] == 0:
            return bad_request(f"El alumno con padrón {padron} ya se encuentra dado de baja en este curso")

        query_baja = """
            UPDATE Curso_has_Usuarios 
            SET Estado = 0
            WHERE Curso_idCurso = %s AND Usuarios_padron = %s
        """
        cursor.execute(query_baja, (idCurso, padron))
        
        funciones.registrar_auditoria(cursor, padron_operador, f"Realizó la baja lógica del alumno {padron} en el curso {idCurso}")
        
        conn.commit()
        return ok_response(f"Alumno con padrón {padron} dado de baja correctamente del curso {idCurso}")
        
    except Exception as e:
        if conn: conn.rollback()
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# GET /api/cursos/<idCurso>/alumnos
# Lista los alumnos inscriptos (únicamente en ese curso)(permite filtrar por estado “activo/abandonó”).
#--------------------------------------------------------------------------------------------------------
@alumnos_bp.route('', methods=['GET'])
def get_alumnos(idCurso):
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return acceso_denegado1("No tiene permisos para ver los alumnos o token inválido")


    estado_filtro = request.args.get('estado') 
    
    conn = None
    cursor = None
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT u.padron, u.nombres, u.mail, chu.Estado 
            FROM Usuarios u
            INNER JOIN Curso_has_Usuarios chu ON u.padron = chu.Usuarios_padron
            WHERE chu.Curso_idCurso = %s AND u.rol = 'Alumno'
        """
        params = [idCurso]
        
        if estado_filtro is not None:
            query += " AND chu.Estado = %s"
            params.append(int(estado_filtro))
            
        cursor.execute(query, params)
        alumnos = cursor.fetchall()
        
        return {"alumnos": alumnos}, 200
        
    except Exception as e:
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# GET /api/cursos/<idCurso>/alumnos/<padron>
# Devuelve la ficha técnica y datos de un alumno en específico notas/ asistencias etc (en el curso específico)
#--------------------------------------------------------------------------------------------------------
@alumnos_bp.route('/<int:padron>', methods=['GET'])
def get_alumno_por_padron(idCurso, padron):
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return acceso_denegado1("No tiene permisos o token inválido")

    conn = None
    cursor = None
    try:
        conn = _get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_usuario = """
            SELECT u.padron, u.nombres, u.mail, chu.Estado 
            FROM Usuarios u
            INNER JOIN Curso_has_Usuarios chu ON u.padron = chu.Usuarios_padron
            WHERE chu.Curso_idCurso = %s AND u.padron = %s AND u.rol = 'Alumno'
        """
        cursor.execute(query_usuario, (idCurso, padron))
        alumno = cursor.fetchone()
        
        if not alumno:
            return not_found(f"Alumno con padrón {padron} no encontrado en el curso {idCurso}")
            

        query_asistencias = """
            SELECT idAsistencia, asistio, fecha, justificado 
            FROM Asistencias 
            WHERE Curso_idCurso = %s AND Usuarios_padron = %s
        """
        cursor.execute(query_asistencias, (idCurso, padron))
        alumno["asistencias"] = cursor.fetchall()
        
        # 3. Notas asignadas en las evaluaciones del curso
        query_notas = """
            SELECT n.idNotas, n.puntaje, e.descripcion AS evaluacion, e.tipo 
            FROM Notas n
            INNER JOIN Evaluaciones e ON n.Evaluaciones_idEvaluacion = e.idEvaluacion
            WHERE e.Curso_idCurso = %s AND n.Usuarios_padron = %s
        """
        cursor.execute(query_notas, (idCurso, padron))
        alumno["notas"] = cursor.fetchall()
        
        return {"alumno": alumno}, 200
        
    except Exception as e:
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# PUT /api/cursos/<idCurso>/alumnos/<padron>
# Modifica datos personales o actualiza el flag de continuidad del alumno en ese curso.
#--------------------------------------------------------------------------------------------------------
@alumnos_bp.route('/<int:padron>', methods=['PUT'])
def put_alumno(idCurso, padron):
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None
    try:
        data = request.get_json(silent=True) or {}
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Actualización de datos en Usuarios
        if "nombres" in data or "mail" in data:
            query_u = "UPDATE Usuarios SET "
            fields = []
            params = []
            if "nombres" in data:
                fields.append("nombres = %s")
                params.append(data["nombres"])
            if "mail" in data:
                if not validaciones.validar_email_fiuba(data["mail"]):
                    return bad_request("El formato del correo es inválido. Debe pertenecer al dominio 'fi.uba.ar'")
                fields.append("mail = %s")
                params.append(data["mail"])
                
            query_u += ", ".join(fields) + " WHERE padron = %s"
            params.append(padron)
            cursor.execute(query_u, params)
            

        if "estado" in data:
            query_rel = "UPDATE Curso_has_Usuarios SET Estado = %s WHERE Curso_idCurso = %s AND Usuarios_padron = %s"
            cursor.execute(query_rel, (int(data["estado"]), idCurso, padron))
            
        funciones.registrar_auditoria(cursor, padron_operador, f"Actualización total (PUT) del alumno {padron} en curso {idCurso}")
        conn.commit()
        
        return ok_response(f"Datos del alumno {padron} reemplazados correctamente")
        
    except Exception as e:
        if conn: conn.rollback()
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# PATCH /api/cursos/<idCurso>/alumnos/<padron>
# Modificación parcial o cambios específicos sobre la ficha del alumno
#--------------------------------------------------------------------------------------------------------
@alumnos_bp.route('/<int:padron>', methods=['PATCH'])
def patch_alumno(idCurso, padron):
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None
    try:
        data = request.get_json(silent=True) or {}
        conn = _get_connection()
        cursor = conn.cursor()
        
        if "nombres" in data or "mail" in data:
            query_u = "UPDATE Usuarios SET "
            fields = []
            params = []
            if "nombres" in data:
                fields.append("nombres = %s")
                params.append(data["nombres"])
            if "mail" in data:
                if not validaciones.validar_email_fiuba(data["mail"]):
                    return bad_request("El correo debe ser del dominio 'fi.uba.ar'")
                fields.append("mail = %s")
                params.append(data["mail"])
                
            query_u += ", ".join(fields) + " WHERE padron = %s"
            params.append(padron)
            cursor.execute(query_u, params)
            
        if "estado" in data:
            query_rel = "UPDATE Curso_has_Usuarios SET Estado = %s WHERE Curso_idCurso = %s AND Usuarios_padron = %s"
            cursor.execute(query_rel, (int(data["estado"]), idCurso, padron))
            
        funciones.registrar_auditoria(cursor, padron_operador, f"Modificación parcial (PATCH) del alumno {padron} en curso {idCurso}")
        conn.commit()
        
        return ok_response(f"Alumno {padron} modificado parcialmente con éxito")
        
    except Exception as e:
        if conn: conn.rollback()
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()