import io
import csv
from db import get_connection
from flask import request, Blueprint
from mysql.connector import IntegrityError
from src.utils.errors import (
    not_found, conflict, server_error, bad_request, ok_response, well_response, unauthorized, acceso_denegado)
from src.utils.validaciones import validar_email_fiuba
from src.utils.seguridad import verify_token

alumnos_bp = Blueprint('alumnos', __name__)

#-------------------------
#Se puededn probar los 3 endpoints si se sacan la autentificacion de rol 
#-------------------------

@alumnos_bp.route('', methods=['POST']) 
def add_alumno(idCurso):
    payload, error, code = verify_token(request)
    if error:
        return error
    
    usuario_rol = payload.get("rol")

    if usuario_rol != "Docente":
        return acceso_denegado("No tiene permisos para agregar alumnos") 
    
    
    conn = None
    cursor = None
    
    try:
        data = request.get_json(silent=True)
        if not data:
            return bad_request("No se recibió un cuerpo JSON válido en la solicitud.")

        # Validación de campos obligatorios 
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

        # Validación mail fiuba
        if not validar_email_fiuba(mail):
            return bad_request("El formato del correo es inválido. Debe pertenecer al dominio 'fi.uba.ar'")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_usuario = """
            INSERT INTO Usuarios (padron, rol, nombres, mail, cursando_actualmente, created_at) 
            VALUES (%s, %s, %s, %s, 1, NOW())
        """
        
        cursor.execute(query_usuario, (padron, rol, nombres, mail))

        query_relacion = """
            INSERT IGNORE INTO Curso_has_Usuarios (Curso_idCurso, Usuarios_padron)
            VALUES (%s, %s)
        """
        cursor.execute(query_relacion, (idCurso, padron))

        conn.commit()
        return well_response(f"Alumno con padrón {padron} agregado correctamente al curso {idCurso}")
    
    except IntegrityError:
        if conn: conn.rollback()
        return conflict("El padrón o correo electrónico ya se encuentra registrado")
    except Exception as e:
        if conn: conn.rollback()
        return server_error(str(e))
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# -------------------------

@alumnos_bp.route('/importar', methods=['POST'])
def importar_alumnos(idCurso):
    payload, error, code = verify_token(request)
    if error:
        return error
    
    usuario_rol = payload.get("rol")

    if usuario_rol != "Docente":
        return acceso_denegado("No tiene permisos para agregar alumnos") 
    
    conn = None
    cursor = None   

    try:
        # Verificar si el archivo viene en la request
        if 'file' not in request.files:
            return bad_request("No se encontró ningún archivo en la solicitud. Asegúrese de enviar el archivo con el campo 'file'.")
            
        file = request.files['file']
        
        #Verificar que el archivo tenga un nombre válido 
        if file.filename == '':
            return bad_request("No se seleccionó ningún archivo para subir.")
        
        # Verificar extensión del archivo
        if not file.filename.endswith('.csv'):
            return bad_request("El archivo debe tener extensión .csv")

       
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream) 
        
        alumnos_a_insertar = []
        campos_esperados = ["padron", "nombres", "mail"]

        # Validar consistencia de datos fila por fila
        for row in csv_input:
            row = {k.strip(): v.strip() for k, v in row.items()}
            
            if not all(campo in row for campo in campos_esperados):
                return bad_request("El archivo CSV debe contener las columnas: padron, nombres, mail")
            
            alumnos_a_insertar.append((
                int(row["padron"]), 
                "Alumno",
                row["nombres"], 
                row["mail"]
                ))

        if not alumnos_a_insertar:
            return bad_request("El archivo CSV está vacío o no contiene registros válidos.")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query_usuario = """
            INSERT INTO Usuarios (padron, rol, nombres, mail, cursando_actualmente, created_at) 
            VALUES (%s, %s, %s, %s, 1, NOW())
            ON DUPLICATE KEY UPDATE cursando_actualmente = 1
        """
        
        cursor.executemany(query_usuario, alumnos_a_insertar)

        relaciones = [(idCurso, alumno[0]) for alumno in alumnos_a_insertar]    

        query_relacion = """
            INSERT IGNORE INTO Curso_has_Usuarios (Curso_idCurso, Usuarios_padron)
            VALUES (%s, %s)
        """
        
        cursor.executemany(query_relacion, relaciones)

        conn.commit()
        registros_insertados = cursor.rowcount

        return well_response(f"Importación finalizada. {registros_insertados} registros insertados o actualizados.")
    
    except IntegrityError:
        return conflict("Uno o más registros en el CSV ya existen (Padrón o Email duplicado).")
    except Exception as e:
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    
#-------------------------

@alumnos_bp.route('/<int:padron>', methods=['DELETE'])
def delete_alumno(idCurso, padron):
    
    payload, error, code = verify_token(request)
    if error:
        return error

    usuario_rol = payload.get("rol")

    if usuario_rol != "Docente":
        return acceso_denegado() 
  

    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Verificar si el alumno está inscrito en este curso y cuál es su estado
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

        # 2. Aplicar la baja lógica cambiando el estado a 'abandonó' solo para esta materia
        query_baja = """
            UPDATE Curso_has_Usuarios 
            SET Estado = 0
            WHERE Curso_idCurso = %s AND Usuarios_padron = %s
        """
        cursor.execute(query_baja, (idCurso, padron))
        conn.commit()
        
        return ok_response(f"Alumno con padrón {padron} dado de baja correctamente del curso {idCurso}")
        
    except Exception as e:
        if conn: conn.rollback()
        return server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
