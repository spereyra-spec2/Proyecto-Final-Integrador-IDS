import mysql.connector
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def get_connection():
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )


def get_equipo(curso_id, usuarios_padron):
    conn = get_connection()
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
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# Para devolver lo cambiado al final aunque el usuario no este en el grupo.
def get_equipo_por_id(equipo_id):
    conn = get_connection()
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
            WHERE equipo.idEquipos = %s
            """,
            (equipo_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def patch_equipo(curso_id, usuarios_padron, data):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        equipo = get_equipo(curso_id, usuarios_padron)
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
        return get_equipo_por_id(equipo_id)

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
        equipo = get_equipo(curso_id, usuarios_padron)
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
