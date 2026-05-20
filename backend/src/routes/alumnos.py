import io
import csv
from db import get_connection
from flask import request, jsonify, Blueprint
from mysql.connector import IntegrityError
from src.utils.funciones import (
    not_found, validar_email_fiuba, conflict, server_error, bad_request
)

alumnos_bp = Blueprint('alumnos', __name__)

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
            return bad_request(f"Faltan campos obligatorios: {', '.join(faltantes)}")

        
        nombres = str(data["nombres"]).strip()
        mail = str(data["mail"]).strip()
        padron = int(data["padron"])
        rol = "estudiantes" 

        # Validación mail fiuba
        if not validar_email_fiuba(mail):
            return bad_request("El formato del correo es inválido. Debe pertenecer al dominio 'fi.uba.ar'")

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
        return conflict("El padrón o correo electrónico ya se encuentra registrado")
    except Exception as e:
        if conn:
            conn.rollback()
        return server_error(str(e))
        
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
                row["padron"], 
                row["nombres"], 
                row["mail"], 
                "estudiantes" 
            ))

        if not alumnos_a_insertar:
            return bad_request("El archivo CSV está vacío o no contiene registros válidos.")
        
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
        return conflict("Uno o más registros en el CSV ya existen (Padrón o Email duplicado).")
    except Exception as e:
        return server_error(str(e))
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
            return not_found(f"No se encontró ningún alumno con el padrón {padron}")
            
        # Verificar si ya se encontraba dado de baja 
        if not alumno['cursando_actualmente']:
            return bad_request(f"El alumno con padrón {padron} ya se encuentra dado de baja")

        
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
        return server_error(str(e))
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
