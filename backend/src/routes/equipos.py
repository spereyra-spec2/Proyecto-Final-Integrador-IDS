from flask import Flask, Blueprint, jsonify, request, url_for, Response, send_file
from src.db.db import get_equipos, crear_equipo, delete_equipo, patch_equipo, get_connection
from src.utils import validaciones as validaciones
from typing import Any
import mysql.connector
from src.utils import errors as errors
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from src.utils import funciones as funciones

equipos_bp = Blueprint("equipos",__name__)

@equipos_bp.route("/<int:curso_id>/equipos", methods = ["GET"])
def obtener_equipos(curso_id: int) -> Response:
    try:
        equipos = get_equipos(curso_id)
        equipos = equipos or []
        return jsonify(equipos), 200
        
    except Exception as e:
        return errors.server_error(str(e))



@equipos_bp.route("/<int:curso_id>/equipos", methods=["POST"])
def registrar_equipo(curso_id: int) -> Response:
    try:
        data = request.get_json()
        
        if not data or "nombre" not in data or "padrones" not in data:
            return errors.bad_request("Faltan campos obligatorios: 'nombre' y 'padrones'")
        
            
        nombre_equipo = data["nombre"]
        padrones = data["padrones"] 
        access_code = data.get("access_code")
        cupo = data.get("cupo")
        
        if not isinstance(padrones, list) or len(padrones) == 0:
            return errors.bad_request("El campo 'padrones' debe ser una lista no vacía")

        crear_equipo(curso_id, {"nombre": nombre_equipo, "access_code": access_code, "cupo": cupo}, padrones)
        
        
        return jsonify({"message": "Equipo creado y alumnos vinculados exitosamente",}), 201
        
    except mysql.connector.Error as db_err:
        return errors.bad_request(f"Error de base de datos (verifique los padrones): {str(db_err)}")
    except Exception as e:
        return errors.server_error(str(e))


@equipos_bp.route('/<int:curso_id>/equipos/join', methods=['POST'])
def join_equipo_by_code(curso_id: int) -> Response:
    try:
        payload = request.get_json()
        if not payload or 'access_code' not in payload or 'padron' not in payload:
            return errors.bad_request("Se requiere 'access_code' y 'padron' en el body")
        access_code = payload['access_code']
        padron = payload['padron']

        nombre_equipo = payload.get('nombre')
        if not nombre_equipo:
            return errors.bad_request("Se requiere 'nombre' del equipo junto con 'access_code' para unirse")

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT idEquipos FROM Equipos WHERE Curso_idCurso = %s AND access_code = %s AND nombre = %s",
            (curso_id, access_code, nombre_equipo),
        )
        equipo = cur.fetchone()
        cur.close(); conn.close()
        if equipo is None:
            return errors.not_found('Código de acceso inválido o equipo no encontrado')

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
                return errors.conflict('El equipo ya alcanzó su cupo máximo')

    
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
                    return errors.not_found('No existe equipo activo para ese curso y referencia')
                return jsonify(equipo_after), 200
            except ValueError as e:
                return errors.bad_request(str(e))
            except Exception as e:
                return errors.server_error(str(e))
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
                    return errors.server_error('Equipo actualizado pero no se pudo recuperar el estado')
                return jsonify(equipo_after), 200
            except Exception as e:
                return errors.server_error(str(e))

    except Exception as e:
        return errors.server_error(str(e))

@equipos_bp.route("/<int:curso_id>/equipos/<int:usuario_padron>", methods=["PATCH"])
def actualizar_equipo(curso_id, usuario_padron):
    try:
        curso_id = validaciones.validar_curso_id(curso_id)
        usuario_padron = validaciones.validar_padron(usuario_padron)
    except ValueError as e:
        return errors.bad_request(str(e))

    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return errors.bad_request("El body debe ser un JSON válido")

    alumno_padron = data.get("alumno_padron")
    activo = data.get("activo")
    equipo_id = data.get("equipo_id")
    evaluacion_id = data.get("evaluacion_id", data.get("tp_id"))

    if equipo_id is None or not isinstance(equipo_id, int) or equipo_id <= 0:
        return errors.bad_request("Debe enviarse un equipo_id válido")

    if alumno_padron is None and evaluacion_id is None:
        return errors.bad_request("Debe enviarse alumno o evaluación")

    if alumno_padron is not None and (not isinstance(alumno_padron, int) or alumno_padron <= 0):
        return errors.bad_request("Padrón inválido")

    if activo is not None and activo not in (0, 1):
        return errors.bad_request("Activo debe ser 0 o 1")

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
            return errors.not_found("Equipo inválido para este curso")

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
        return errors.server_error(str(e))


@equipos_bp.route("/<int:curso_id>/equipos/<int:usuario_padron>", methods=["DELETE"])
def disolver_equipo(curso_id, usuario_padron):
    try:
        curso_id = validaciones.validar_curso_id(curso_id)
        usuario_padron = validaciones.validar_padron(usuario_padron)
    except ValueError as e:
        return errors.bad_request(str(e))
    try:
        eliminado = delete_equipo(curso_id, usuario_padron)
        if not eliminado:
            return errors.not_found("No existe un equipo activo para ese curso y padrón.")

        return jsonify({"message": "Equipo disuelto correctamente."}), 200

    except Exception as e:
        return errors.server_error(e)

@equipos_bp.route('/<int:idCurso>/reporte-equipos', methods=['GET'])
def reporte_equipos_pdf(idCurso):
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)

    sin_equipo = request.args.get('sin_equipo', 'excluir')

    conn = None
    cursor = None

    alumnos_sueltos = []

    try:
        equipos = get_equipos(idCurso)
    
        if sin_equipo == 'incluir':
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query_sueltos = """
                SELECT u.padron, u.nombres, u.mail 
                FROM Usuarios u
                INNER JOIN Curso_has_Usuarios chu ON u.padron = chu.Usuarios_padron
                WHERE chu.Curso_idCurso = %s 
                  AND chu.Estado = 1 
                  AND u.rol = 'Alumno'
                  AND u.padron NOT IN (
                      SELECT uhe.Usuarios_padron 
                      FROM Usuarios_has_Equipos uhe
                      INNER JOIN Equipos e ON uhe.Equipos_idEquipos = e.idEquipos
                      WHERE e.Curso_idCurso = %s 
                        AND uhe.activo = 1
                  )
            """
            cursor.execute(query_sueltos, (idCurso, idCurso))
            alumnos_sueltos = cursor.fetchall()
            
            funciones.registrar_auditoria(cursor, padron_operador, f"Exportó PDF de equipos del curso {idCurso}")
            conn.commit()
            
    except Exception as e:
        return errors.server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()
    
    story.append(Paragraph("<b>ACADEMIQ - REPORTE DE EQUIPOS</b>", styles['Heading1']))
    story.append(Paragraph(f"Curso ID: {idCurso} | Alumnos sin grupo: {sin_equipo.upper()}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2d5986")), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    if equipos:
        for eq in equipos_lista:
            story.append(Paragraph(f"<b>🔹 Equipo: {eq['nombre']}</b> (Código: {eq['access_code'] or '—'})", styles['Heading3']))
            story.append(Spacer(1, 5))
            
            tabla_datos = [["Padrón", "Nombre y Apellido", "Correo Electrónico"]]
            
            for miembro in eq.get('integrantes', []):
                if int(miembro.get('activo', 0)) == 1:
                    tabla_datos.append([
                        str(miembro['padron']),
                        miembro.get('nombre', '—'), 
                        miembro.get('mail', '—')     
                    ])
                
            if len(tabla_datos) == 1:
                tabla_datos.append(["—", "Este equipo no tiene integrantes activos", "—"])
                
            tabla_pdf = Table(tabla_datos, colWidths=[70, 230, 230])
            tabla_pdf.setStyle(estilo_tabla)
            story.append(tabla_pdf)
            story.append(Spacer(1, 15))
    else:
        story.append(Paragraph("No hay equipos registrados en este curso.", styles['Normal']))
        story.append(Spacer(1, 15))
        
    if sin_equipo == 'incluir' and alumnos_sueltos:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>⚠️ Alumnos sin Equipo Asignado</b>", styles['Heading3']))
        story.append(Spacer(1, 5))
        
        tabla_sueltos_datos = [["Padrón", "Nombre y Apellido", "Correo Electrónico"]]
        for alu in alumnos_sueltos:
            tabla_sueltos_datos.append([
                str(alu['padron']),
                alu['nombres'], 
                alu['mail']
            ])
            
        tabla_sueltos_pdf = Table(tabla_sueltos_datos, colWidths=[70, 230, 230])
        
        estilo_sueltos = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b33939")), 
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff5f5")]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        tabla_sueltos_pdf.setStyle(estilo_sueltos)
        story.append(tabla_sueltos_pdf)

    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=f'reporte_equipos_curso_{idCurso}.pdf'
    )