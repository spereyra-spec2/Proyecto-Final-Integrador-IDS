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

def patch_equipo(curso_id, usuarios_padron, data):
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                equipo.idEquipos AS id,
                equipo.nombre,
                equipo.created_at,
                equipo.curso_idcurso AS curso_id
            FROM equipos AS equipo
            INNER JOIN usuarios_has_equipos AS user_has_equipo
                ON user_has_equipo.equipos_idequipos = equipo.idEquipos
            WHERE equipo.curso_idcurso = %s
              AND user_has_equipo.usuarios_padron = %s
              AND COALESCE(user_has_equipo.activo, 1) = 1
            """,
            (curso_id, usuarios_padron),
        )
        equipo = cursor.fetchone()
        if equipo is None:
            return None

        equipo_id = equipo["id"]

        alumno_padron = data.get("alumno_padron")
        activo = data.get("activo")
        tp_id = data.get("tp_id", data.get("evaluacion_id"))

        if alumno_padron is not None:
            if activo == 0:
                cursor.execute(
                    """
                    UPDATE usuarios_has_equipos
                    SET activo = 0,
                        activo_hasta = NOW()
                    WHERE equipos_idequipos = %s
                      AND usuarios_padron = %s
                      AND COALESCE(activo, 1) = 1
                    """,
                    (equipo_id, alumno_padron)
                )

            elif activo == 1:
                cursor.execute(
                    """
                    UPDATE usuarios_has_equipos AS user_has_equipo
                        INNER JOIN equipos AS equipo
                        ON equipo.idEquipos = user_has_equipo.equipos_idequipos
                    SET user_has_equipo.activo = 0,
                        user_has_equipo.activo_hasta = NOW()
                    WHERE user_has_equipo.usuarios_padron = %s
                      AND equipo.curso_idcurso = %s
                      AND user_has_equipo.equipos_idequipos <> %s
                      AND COALESCE(user_has_equipo.activo, 1) = 1
                    """,
                    (alumno_padron, curso_id, equipo_id)
                )

                cursor.execute(
                    """
                    UPDATE usuarios_has_equipos AS user_has_equipo
                        INNER JOIN equipos AS equipo
                        ON equipo.idEquipos = user_has_equipo.equipos_idequipos
                    SET user_has_equipo.activo       = 1,
                        user_has_equipo.activo_desde = COALESCE(user_has_equipo.activo_desde, NOW()),
                        user_has_equipo.activo_hasta = NULL
                    WHERE user_has_equipo.equipos_idequipos = %s
                      AND user_has_equipo.usuarios_padron = %s
                      AND equipo.curso_idcurso = %s
                    """,
                    (equipo_id, alumno_padron, curso_id)
                )

                if cursor.rowcount == 0:
                    cursor.execute(
                        """
                        INSERT INTO usuarios_has_equipos (
                            usuarios_padron,
                            equipos_idequipos,
                            activo,
                            activo_desde,
                            activo_hasta
                        )
                        VALUES (%s, %s, 1, NOW(), NULL)
                        """,
                        (alumno_padron, equipo_id)
                    )

        if tp_id is not None:
            cursor.execute(
                """
                UPDATE equipos_has_evaluaciones
                SET Evaluaciones_idEvaluacion = %s
                WHERE Equipos_idEquipos = %s
                """,
                (tp_id, equipo_id)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO equipos_has_evaluaciones (
                        Equipos_idEquipos,
                        Evaluaciones_idEvaluacion
                    )
                    VALUES (%s, %s)
                    """,
                    (equipo_id, tp_id)
                )

        conn.commit()

        cursor.execute(
            """
            SELECT
                equipo.idEquipos AS id,
                equipo.nombre,
                equipo.created_at,
                equipo.curso_idcurso AS curso_id
            FROM equipos AS equipo
            WHERE equipo.idEquipos = %s
            """,
            (equipo_id,),
        )
        return cursor.fetchone()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def delete_equipo(curso_id, usuarios_padron):
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                equipo.idEquipos AS id
            FROM equipos AS equipo
            INNER JOIN usuarios_has_equipos AS user_has_equipo
                ON user_has_equipo.equipos_idequipos = equipo.idEquipos
            WHERE equipo.curso_idcurso = %s
              AND user_has_equipo.usuarios_padron = %s
              AND COALESCE(user_has_equipo.activo, 1) = 1
            """,
            (curso_id, usuarios_padron),
        )
        equipo = cursor.fetchone()
        if equipo is None:
            return False

        equipo_id = equipo["id"]

        cursor.execute(
            """
            UPDATE usuarios_has_equipos
            SET activo       = 0,
                activo_hasta = NOW()
            WHERE equipos_idequipos = %s
              AND COALESCE(activo, 1) = 1
            """,
            (equipo_id,)
        )

        cursor.execute(
            """
            DELETE FROM equipos_has_evaluaciones
            WHERE Equipos_idEquipos = %s
            """,(equipo_id,)
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
