import mysql.connector
import sys
import os
import hashlib
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
import config


def _get_connection():
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )


def crear_equipo(curso_id: int, nombre_equipo: str, padrones: list) -> str:
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        '''
        seed = f"{nombre_equipo}-{time.time()}".encode("utf-8")
        hash_completo = hashlib.md5(semilla).hexdigest()
        codigo_acceso = hash_completo[:8].upper()  
        '''
        query_equipo = """
            INSERT INTO equipos (nombre, curso_idcurso, created_at) 
            VALUES (%s, %s, NOW());
        """
        cursor.execute(query_equipo, (nombre_equipo, curso_id))
        
    
        id_nuevo_equipo = cursor.lastrowid
    
        query_vincular_usuarios_a_equipo = """
            INSERT INTO usuarios_has_equipos (usuarios_padron, equipos_idequipos, activo, activo_desde)
            VALUES (%s, %s, 1, NOW());
        """
        
        for padron in padrones:
            cursor.execute(query_vincular_usuarios_a_equipo, (padron, id_nuevo_equipo))
            
    
        conn.commit()
        

    except mysql.connector.Error as err:

        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


def get_equipos(curso_id: int) -> list:
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT 
                e.idEquipos, 
                e.nombre AS equipo_nombre,
                u.padron, 
                u.nombres AS usuario_nombre
            FROM equipos e
            LEFT JOIN usuarios_has_equipos uhe ON e.idEquipos = uhe.equipos_idequipos AND uhe.activo = 1
            LEFT JOIN usuarios u ON uhe.usuarios_padron = u.padron
            WHERE e.curso_idcurso = %s;
        """
        
    cursor.execute(query, (curso_id,))
    resultados = cursor.fetchall()
        
    cursor.close()
    conn.close()

    equipos_dict = {}
    for fila in resultados:
        id_equipo = fila["idEquipos"]
        
        if id_equipo not in equipos_dict:
            equipos_dict[id_equipo] = {
                "idEquipos": id_equipo,
                "nombre": fila["equipo_nombre"],
                "integrantes": []
            }
        
        if fila["padron"] is not None:
            equipos_dict[id_equipo]["integrantes"].append({
                "padron": fila["padron"],
                "nombre": fila["usuario_nombre"]
            })

    return list(equipos_dict.values())