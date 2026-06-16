from flask import Flask, Blueprint, jsonify, request, url_for, Response
from src.db.db import get_equipos, crear_equipo, delete_equipo, patch_equipo, get_connection
from src.utils.validaciones import validar_curso_datos, validar_entero, validar_curso_id, validar_padron
from typing import Any
import mysql.connector
from src.utils.errors import error_response, not_found, bad_request, server_error, conflict

equipos_bp = Blueprint("equipos",__name__)

@equipos_bp.route("/<int:curso_id>/equipos", methods = ["GET"])
def obtener_equipos(curso_id: int) -> Response:
    try:
        equipos = get_equipos(curso_id)
        equipos = equipos or []
        return jsonify(equipos), 200
        
    except Exception as e:
        return server_error(str(e))



@equipos_bp.route("/<int:curso_id>/equipos", methods=["POST"])
def registrar_equipo(curso_id: int) -> Response:
    try:
        data = request.get_json()
        
        if not data or "nombre" not in data or "padrones" not in data:
            return bad_request("Faltan campos obligatorios: 'nombre' y 'padrones'")
        
            
        nombre_equipo = data["nombre"]
        padrones = data["padrones"] 
        access_code = data.get("access_code")
        cupo = data.get("cupo")
        
        if not isinstance(padrones, list) or len(padrones) == 0:
            return bad_request("El campo 'padrones' debe ser una lista no vacía")

        crear_equipo(curso_id, {"nombre": nombre_equipo, "access_code": access_code, "cupo": cupo}, padrones)
        
        
        return jsonify({"message": "Equipo creado y alumnos vinculados exitosamente",}), 201
        
    except mysql.connector.Error as db_err:
        return bad_request(f"Error de base de datos (verifique los padrones): {str(db_err)}")
    except Exception as e:
        return server_error(str(e))


@equipos_bp.route('/<int:curso_id>/equipos/join', methods=['POST'])
def join_equipo_by_code(curso_id: int) -> Response:
    try:
        payload = request.get_json()
        if not payload or 'access_code' not in payload or 'padron' not in payload:
            return bad_request("Se requiere 'access_code' y 'padron' en el body")
        access_code = payload['access_code']
        padron = payload['padron']

        nombre_equipo = payload.get('nombre')
        if not nombre_equipo:
            return bad_request("Se requiere 'nombre' del equipo junto con 'access_code' para unirse")

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT idEquipos FROM Equipos WHERE Curso_idCurso = %s AND access_code = %s AND nombre = %s",
            (curso_id, access_code, nombre_equipo),
        )
        equipo = cur.fetchone()
        cur.close(); conn.close()
        if equipo is None:
            return not_found('Código de acceso inválido o equipo no encontrado')

        equipo_id = equipo['idEquipos']

    
        conn_c = get_connection()
        cur_c = conn_c.cursor(dictionary=True)
        cur_c.execute("""
            SELECT e.cupo AS cupo, SUM(COALESCE(uhe.activo,0)) AS active_count
            FROM Equipos e
            LEFT JOIN Usuarios_has_Equipos uhe ON e.idEquipos = uhe.Equipos_idEquipos
            WHERE e.idEquipos = %s
            GROUP BY e.idEquipos
        """, (equipo_id,))
        seat_info = cur_c.fetchone()
        cur_c.close(); conn_c.close()
        if seat_info:
            cupo_val = seat_info.get('cupo')
            active_count = int(seat_info.get('active_count') or 0)
            if cupo_val is not None and active_count >= int(cupo_val):
                return conflict('El equipo ya alcanzó su cupo máximo')

    
        conn2 = get_connection()
        cur2 = conn2.cursor(dictionary=True)
        cur2.execute("SELECT Usuarios_padron FROM Usuarios_has_Equipos WHERE Equipos_idEquipos = %s AND COALESCE(activo,1)=1 LIMIT 1", (equipo_id,))
        ref = cur2.fetchone()
        cur2.close(); conn2.close()

        if ref:
            reference_padron = ref.get('Usuarios_padron')
            try:
                equipo_after = patch_equipo(curso_id, int(reference_padron), {"alumno_padron": int(padron), "activo": 1})
                if equipo_after is None:
                    return not_found('No existe equipo activo para ese curso y referencia')
                return jsonify(equipo_after), 200
            except ValueError as e:
                return bad_request(str(e))
            except Exception as e:
                return server_error(str(e))
        else:
            try:
                conn_ins = get_connection()
                cur_ins = conn_ins.cursor()
                cur_ins.execute("SELECT COALESCE(activo,0) AS activo FROM Usuarios_has_Equipos WHERE Equipos_idEquipos = %s AND Usuarios_padron = %s", (equipo_id, int(padron)))
                existing = cur_ins.fetchone()
                if existing:
                    cur_ins.execute(
                        """
                        UPDATE Usuarios_has_Equipos
                        SET activo = 1,
                            activo_desde = COALESCE(activo_desde, NOW()),
                            activo_hasta = NULL
                        WHERE Equipos_idEquipos = %s AND Usuarios_padron = %s
                        """,
                        (equipo_id, int(padron)),
                    )
                else:
                    cur_ins.execute(
                        """
                        INSERT INTO Usuarios_has_Equipos (Usuarios_padron, Equipos_idEquipos, activo, activo_desde)
                        VALUES (%s, %s, 1, NOW())
                        """,
                        (int(padron), equipo_id),
                    )
                conn_ins.commit()
                cur_ins.close(); conn_ins.close()

                
                equipos = get_equipos(curso_id)
                equipo_after = None
                for e in equipos:
                    if e.get('idEquipos') == equipo_id:
                        equipo_after = e
                        break
                if equipo_after is None:
                    return server_error('Equipo actualizado pero no se pudo recuperar el estado')
                return jsonify(equipo_after), 200
            except Exception as e:
                return server_error(str(e))

    except Exception as e:
        return server_error(str(e))

@equipos_bp.route("/<int:curso_id>/equipos/<int:usuario_padron>", methods=["PATCH"])
def actualizar_equipo(curso_id, usuario_padron):
    try:
        curso_id = validar_curso_id(curso_id)
        usuario_padron = validar_padron(usuario_padron)
    except ValueError as e:
        return bad_request(str(e))

    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return bad_request("El body debe ser un JSON válido")

    alumno_padron = data.get("alumno_padron")
    activo = data.get("activo")
    equipo_id = data.get("equipo_id")
    evaluacion_id = data.get("evaluacion_id", data.get("tp_id"))

    if equipo_id is None or not isinstance(equipo_id, int) or equipo_id <= 0:
        return bad_request("Debe enviarse un equipo_id válido")

    if alumno_padron is None and evaluacion_id is None:
        return bad_request("Debe enviarse alumno o evaluación")

    if alumno_padron is not None and (not isinstance(alumno_padron, int) or alumno_padron <= 0):
        return bad_request("Padrón inválido")

    if activo is not None and activo not in (0, 1):
        return bad_request("Activo debe ser 0 o 1")

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT idEquipos
            FROM Equipos
            WHERE idEquipos = %s AND Curso_idCurso = %s
            """,
            (equipo_id, curso_id),
        )

        if cur.fetchone() is None:
            cur.close()
            conn.close()
            return not_found("Equipo inválido para este curso")

        if alumno_padron is not None:

            if activo == 0:
                cur.execute(
                    """
                    UPDATE Usuarios_has_Equipos
                    SET activo = 0,
                        activo_hasta = NOW()
                    WHERE Usuarios_padron = %s
                      AND Equipos_idEquipos = %s
                      AND activo = 1
                    """,
                    (alumno_padron, equipo_id),
                )

            elif activo == 1:
                cur.execute(
                    """
                    UPDATE Usuarios_has_Equipos
                    SET activo = 0,
                        activo_hasta = NOW()
                    WHERE Usuarios_padron = %s
                      AND activo = 1
                      AND Equipos_idEquipos <> %s
                    """,
                    (alumno_padron, equipo_id),
                )

                cur.execute(
                    """
                    UPDATE Usuarios_has_Equipos
                    SET activo = 1,
                        activo_desde = COALESCE(activo_desde, NOW()),
                        activo_hasta = NULL
                    WHERE Usuarios_padron = %s
                      AND Equipos_idEquipos = %s
                    """,
                    (alumno_padron, equipo_id),
                )

                if cur.rowcount == 0:
                    cur.execute(
                        """
                        INSERT INTO Usuarios_has_Equipos
                        (Usuarios_padron, Equipos_idEquipos, activo, activo_desde)
                        VALUES (%s, %s, 1, NOW())
                        """,
                        (alumno_padron, equipo_id),
                    )

        if evaluacion_id is not None:
            cur.execute(
                """
                UPDATE Equipos_has_Evaluaciones
                SET Evaluaciones_idEvaluacion = %s
                WHERE Equipos_idEquipos = %s
                """,
                (evaluacion_id, equipo_id),
            )

            if cur.rowcount == 0:
                cur.execute(
                    """
                    INSERT INTO Equipos_has_Evaluaciones
                    (Equipos_idEquipos, Evaluaciones_idEvaluacion)
                    VALUES (%s, %s)
                    """,
                    (equipo_id, evaluacion_id),
                )

        conn.commit()
        cur.execute(
            """
            SELECT idEquipos, nombre, created_at, Curso_idCurso AS curso_id
            FROM Equipos
            WHERE idEquipos = %s
            """,
            (equipo_id,),
        )

        equipo = cur.fetchone()

        cur.close()
        conn.close()

        return jsonify(equipo), 200

    except Exception as e:
        return server_error(str(e))


@equipos_bp.route("/<int:curso_id>/equipos/<int:usuario_padron>", methods=["DELETE"])
def disolver_equipo(curso_id, usuario_padron):
    try:
        curso_id = validar_curso_id(curso_id)
        usuario_padron = validar_padron(usuario_padron)
    except ValueError as e:
        return bad_request(str(e))
    try:
        eliminado = delete_equipo(curso_id, usuario_padron)
        if not eliminado:
            return not_found("No existe un equipo activo para ese curso y padrón.")

        return jsonify({"message": "Equipo disuelto correctamente."}), 200

    except Exception as e:
        return server_error(e)
