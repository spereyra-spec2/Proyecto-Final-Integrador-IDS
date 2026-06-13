import os
import sys
import mysql.connector
import hashlib
import time

DB_DIR = os.path.dirname(os.path.abspath(__file__))

BACKEND_DIR = os.path.abspath(os.path.join(DB_DIR, '..', '..'))

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


import config

def get_connection():
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )


def crear_equipo(curso_id: int, nombre_equipo: str, padrones: list) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        
        query_equipo = """
            INSERT INTO Equipos (nombre, Curso_idCurso, created_at, access_code, cupo) 
            VALUES (%s, %s, NOW(), %s, %s);
        """
        access_code = None
        cupo = None
        if isinstance(nombre_equipo, dict):
            access_code = nombre_equipo.get('access_code')
            cupo = nombre_equipo.get('cupo')
            nombre = nombre_equipo.get('nombre')
        else:
            nombre = nombre_equipo

        # cupo default = 4
        try:
            cupo_val = int(cupo) if cupo is not None and cupo != '' else None
        except Exception:
            cupo_val = None

        if cupo_val is None:
            cupo_val = 4

        cursor.execute(query_equipo, (nombre, curso_id, access_code, cupo_val))
        
        id_nuevo_equipo = cursor.lastrowid
    
        
        query_vincular_usuarios_a_equipo = """
            INSERT INTO Usuarios_has_Equipos (Usuarios_padron, Equipos_idEquipos, activo, activo_desde)
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
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
            SELECT 
                e.idEquipos, 
                e.nombre AS equipo_nombre,
                    e.access_code AS access_code,
                u.padron, 
                u.nombres AS usuario_nombre,
                uhe.activo,
                uhe.activo_desde,
                uhe.activo_hasta,
                e.cupo AS cupo
            FROM Equipos e
            LEFT JOIN Usuarios_has_Equipos uhe ON e.idEquipos = uhe.Equipos_idEquipos
            LEFT JOIN Usuarios u ON uhe.Usuarios_padron = u.padron
            WHERE e.Curso_idCurso = %s
            ORDER BY e.idEquipos, uhe.activo DESC, uhe.activo_desde ASC;
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
                "nombre": fila["usuario_nombre"],
                "activo": int(fila.get("activo") or 0),
                "activo_desde": fila.get("activo_desde"),
                "activo_hasta": fila.get("activo_hasta"),
            })

        
        equipos_dict[id_equipo]["cupo"] = fila.get("cupo")
        equipos_dict[id_equipo]["access_code"] = fila.get("access_code")

    
    for t in equipos_dict.values():
        integrantes = t.get('integrantes') or []
        t['active_count'] = sum(1 for m in integrantes if int(m.get('activo') or 0) == 1)

    return list(equipos_dict.values())


def patch_equipo(curso_id, usuarios_padron, data):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        
        cursor.execute(
            """
            SELECT
                equipo.idEquipos AS id,
                equipo.nombre,
                equipo.created_at,
                equipo.Curso_idCurso AS curso_id
            FROM Equipos AS equipo
            INNER JOIN Usuarios_has_Equipos AS user_has_equipo
                ON user_has_equipo.Equipos_idEquipos = equipo.idEquipos
            WHERE equipo.Curso_idCurso = %s
              AND user_has_equipo.Usuarios_padron = %s
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
                    UPDATE Usuarios_has_Equipos
                    SET activo = 0,
                        activo_hasta = NOW()
                    WHERE Equipos_idEquipos = %s
                      AND Usuarios_padron = %s
                      AND COALESCE(activo, 1) = 1
                    """,
                    (equipo_id, alumno_padron)
                )

            elif activo == 1:
                
                cursor.execute(
                    """
                    UPDATE Usuarios_has_Equipos AS user_has_equipo
                        INNER JOIN Equipos AS equipo
                        ON equipo.idEquipos = user_has_equipo.Equipos_idEquipos
                    SET user_has_equipo.activo = 0,
                        user_has_equipo.activo_hasta = NOW()
                    WHERE user_has_equipo.Usuarios_padron = %s
                      AND equipo.Curso_idCurso = %s
                      AND user_has_equipo.Equipos_idEquipos <> %s
                      AND COALESCE(user_has_equipo.activo, 1) = 1
                    """,
                    (alumno_padron, curso_id, equipo_id)
                )

                cursor.execute(
                    """
                    UPDATE Usuarios_has_Equipos AS user_has_equipo
                        INNER JOIN Equipos AS equipo
                        ON equipo.idEquipos = user_has_equipo.Equipos_idEquipos
                    SET user_has_equipo.activo       = 1,
                        user_has_equipo.activo_desde = COALESCE(user_has_equipo.activo_desde, NOW()),
                        user_has_equipo.activo_hasta = NULL
                    WHERE user_has_equipo.Equipos_idEquipos = %s
                      AND user_has_equipo.Usuarios_padron = %s
                      AND equipo.Curso_idCurso = %s
                    """,
                    (equipo_id, alumno_padron, curso_id)
                )

                if cursor.rowcount == 0:
                    cursor.execute(
                        """
                        INSERT INTO Usuarios_has_Equipos (
                            Usuarios_padron,
                            Equipos_idEquipos,
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
                UPDATE Equipos_has_Evaluaciones
                SET Evaluaciones_idEvaluacion = %s
                WHERE Equipos_idEquipos = %s
                """,
                (tp_id, equipo_id)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO Equipos_has_Evaluaciones (
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
                equipo.Curso_idCurso AS curso_id
            FROM Equipos AS equipo
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
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        
        cursor.execute(
            """
            SELECT
                equipo.idEquipos AS id
            FROM Equipos AS equipo
            INNER JOIN Usuarios_has_Equipos AS user_has_equipo
                ON user_has_equipo.Equipos_idEquipos = equipo.idEquipos
            WHERE equipo.Curso_idCurso = %s
              AND user_has_equipo.Usuarios_padron = %s
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
            UPDATE Usuarios_has_Equipos
            SET activo       = 0,
                activo_hasta = NOW()
            WHERE Equipos_idEquipos = %s
              AND COALESCE(activo, 1) = 1
            """,
            (equipo_id,)
        )

        cursor.execute(
            """
            DELETE FROM Equipos_has_Evaluaciones
            WHERE Equipos_idEquipos = %s
            """, (equipo_id,)
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
