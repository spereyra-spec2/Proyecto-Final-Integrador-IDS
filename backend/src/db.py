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


def list_equipos_por_curso(curso_id):
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
            WHERE equipo.curso_idcurso = %s
            """,
            (curso_id,),
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            equipo_id = r["id"]
            cursor.execute(
                """
                SELECT usuarios_padron
                FROM usuarios_has_equipos
                WHERE equipos_idequipos = %s
                  AND COALESCE(activo, 1) = 1
                """,
                (equipo_id,),
            )
            pads = [str(p["usuarios_padron"]) for p in cursor.fetchall()]
            result.append({
                "id": str(equipo_id),
                "nombre": r.get("nombre"),
                "curso_id": r.get("curso_id"),
                "codigo_acceso": f"EQ{int(equipo_id):06d}",
                "cupo_maximo": 5,
                "integrantes": pads,
                "created_at": r.get("created_at"),
            })
        return result
    finally:
        cursor.close()
        conn.close()


def create_equipo_por_curso(curso_id, nombre, cupo_maximo=5):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO equipos (nombre, created_at, curso_idcurso)
            VALUES (%s, NOW(), %s)
            """,
            (nombre, curso_id),
        )
        conn.commit()
        equipo_id = cursor.lastrowid
        return {
            "id": str(equipo_id),
            "nombre": nombre,
            "curso_id": curso_id,
            "codigo_acceso": f"EQ{int(equipo_id):06d}",
            "cupo_maximo": cupo_maximo,
            "integrantes": [],
        }
    finally:
        cursor.close()
        conn.close()


def sync_integrantes_por_equipo(equipo_id, integrantes):
    """Sincroniza la lista de integrantes de un equipo: activa los pads presentes
    y marca inactivos los que no están en la lista."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Obtener pads existentes (tanto activos como inactivos)
        cursor.execute(
            """
            SELECT usuarios_padron, COALESCE(activo,1) as activo
            FROM usuarios_has_equipos
            WHERE equipos_idequipos = %s
            """,
            (equipo_id,),
        )
        rows = cursor.fetchall()
        existing = {r[0]: r[1] for r in rows}

        target_set = set(int(p) for p in integrantes)

        # Desactivar los que ya no deben estar
        for padron, activo in existing.items():
            if padron not in target_set and activo == 1:
                cursor.execute(
                    """
                    UPDATE usuarios_has_equipos
                    SET activo = 0, activo_hasta = NOW()
                    WHERE equipos_idequipos = %s AND usuarios_padron = %s
                    """,
                    (equipo_id, padron),
                )

        # Activar o insertar los que deben estar
        for padron in target_set:
            if padron in existing:
                # actualizar si está inactivo
                if existing[padron] != 1:
                    cursor.execute(
                        """
                        UPDATE usuarios_has_equipos
                        SET activo = 1, activo_desde = COALESCE(activo_desde, NOW()), activo_hasta = NULL
                        WHERE equipos_idequipos = %s AND usuarios_padron = %s
                        """,
                        (equipo_id, padron),
                    )
            else:
                cursor.execute(
                    """
                    INSERT INTO usuarios_has_equipos (
                        usuarios_padron, equipos_idequipos, activo, activo_desde, activo_hasta
                    ) VALUES (%s, %s, 1, NOW(), NULL)
                    """,
                    (padron, equipo_id),
                )

        conn.commit()
        # Devolver estado actualizado
        cursor.execute(
            """
            SELECT usuarios_padron
            FROM usuarios_has_equipos
            WHERE equipos_idequipos = %s AND COALESCE(activo,1) = 1
            """,
            (equipo_id,),
        )
        pads = [str(r[0]) for r in cursor.fetchall()]
        return pads
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_equipo_por_id(equipo_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE usuarios_has_equipos
            SET activo = 0, activo_hasta = NOW()
            WHERE equipos_idequipos = %s AND COALESCE(activo,1) = 1
            """,
            (equipo_id,),
        )

        cursor.execute(
            """
            DELETE FROM equipos_has_evaluaciones
            WHERE Equipos_idEquipos = %s
            """,
            (equipo_id,),
        )

        cursor.execute(
            """
            DELETE FROM equipos
            WHERE idEquipos = %s
            """,
            (equipo_id,),
        )

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def list_students_por_curso(curso_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.padron, u.nombres AS nombre
            FROM usuarios u
            INNER JOIN curso_has_usuarios cu ON cu.usuarios_padron = u.padron
            WHERE cu.curso_idcurso = %s
            """,
            (curso_id,),
        )
        rows = cursor.fetchall()
        return [{"padron": str(r["padron"]), "nombre": r["nombre"]} for r in rows]
    finally:
        cursor.close()
        conn.close()


def get_course_info(curso_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT idCurso AS id, nombre, descripcion
            FROM curso
            WHERE idCurso = %s
            """,
            (curso_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        # No hay campo 'codigo' en la tabla; construir uno simple
        return {"id": row.get("id"), "nombre": row.get("nombre"), "codigo": f"C{int(row.get('id')):04d}"}
    finally:
        cursor.close()
        conn.close()
