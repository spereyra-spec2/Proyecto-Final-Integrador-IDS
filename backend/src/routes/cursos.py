import io
from flask import Blueprint, request, jsonify, send_file
from pymysql import IntegrityError
from src.db.db import get_connection
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import src.utils.errors as errors
import src.utils.validaciones as validaciones
import src.utils.funciones as funciones

cursos_bp = Blueprint('cursos', __name__)


#--------------------------------------------------------------------------------------------------------
# GET /api/cursos/{idCurso}/reporte-alumnos
# Genera y exporta un documento PDF con la lista de alumnos de un curso
#--------------------------------------------------------------------------------------------------------
@cursos_bp.route('/<int:idCurso>/reporte-alumnos', methods=['GET'])
def reporte_alumnos_pdf(idCurso):

    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    ordenar_por = request.args.get('ordenar_por', 'apellido')
    filtrar_activos = request.args.get('filtrar_activos', 'todos')

    query = """
        SELECT u.padron, u.nombres, u.mail, chu.Estado 
        FROM Usuarios u
        INNER JOIN Curso_has_Usuarios chu ON u.padron = chu.Usuarios_padron
        WHERE chu.Curso_idCurso = %s AND u.rol = 'Alumno'
    """
    
    if filtrar_activos == 'activos':
        query += " AND chu.Estado = 1"
        
    if ordenar_por == 'padron':
        query += " ORDER BY u.padron ASC"
    else:
        query += " ORDER BY u.nombres ASC"
        
    alumnos_lista = []
    conn = None
    cursor = None
    

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (idCurso,))
        alumnos_lista = cursor.fetchall()
        
        funciones.registrar_auditoria(cursor, padron_operador, f"Exportó PDF de alumnos del curso {idCurso}")
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
    
    story.append(Paragraph("<b>ACADEMIQ - REPORTE GENERAL DE ALUMNOS</b>", styles['Heading1']))
    story.append(Paragraph(f"Curso ID: {idCurso} | Criterio: {ordenar_por.upper()} | Estado: {filtrar_activos.upper()}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    tabla_datos = [["Padrón", "Nombre y Apellido", "Correo Electrónico", "Estado"]]
    
    for alu in alumnos_lista:
        estado_texto = "Activo" if alu['Estado'] == 1 else "Inactivo"
        tabla_datos.append([
            str(alu['padron']),
            alu['nombres'],
            alu['mail'],
            estado_texto
        ])
        
    tabla_pdf = Table(tabla_datos, colWidths=[70, 180, 200, 80])
    
    tabla_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2d5986")), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(tabla_pdf)
    doc.build(story)
    
    buffer.seek(0)
    
    return send_file(
        buffer, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=f'reporte_alumnos_curso_{idCurso}.pdf'
    )

#--------------------------------------------------------------------------------------------------------
# GET /api/cursos/{idCurso}/reporte-estadisticias
# Genera y exporta un documento PDF con el porcentaje de aprobados de un curso
#--------------------------------------------------------------------------------------------------------
@cursos_bp.route('/<int:idCurso>/reporte-estadisticas', methods=['GET'])
def reporte_rendimiento_general_pdf(idCurso):
    
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)

    # Traigo el promedio obtenido de todas las evaluaciones solamente si el alumno esta activo
    query = """
        SELECT 
            u.padron, 
            u.nombres, 
            AVG(n.puntaje) AS promedio_final
        FROM Usuarios u
        INNER JOIN Curso_has_Usuarios chu ON u.padron = chu.Usuarios_padron
        INNER JOIN Notas n ON u.padron = n.Usuarios_padron
        INNER JOIN Evaluaciones e ON n.Evaluaciones_idEvaluacion = e.idEvaluacion
        WHERE chu.Curso_idCurso = %s AND e.Curso_idCurso = %s AND chu.Estado = 1
        GROUP BY u.padron, u.nombres
        ORDER BY u.nombres ASC
    """
    
    alumnos_promedios = []
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (idCurso, idCurso))
        alumnos_promedios = cursor.fetchall()
        
        funciones.registrar_auditoria(cursor, padron_operador, f"Exportó PDF del índice de aprobación del curso {idCurso}")
        conn.commit()
    except Exception as e:
        return errors.server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    total_alumnos = len(alumnos_promedios)
    aprobados = 0
    
    # Asumo que para aprobar se deberá tener un promedio >= 4
    for alu in alumnos_promedios:
        if float(alu['promedio_final']) >= 4.0:
            aprobados += 1
            
    desaprobados = total_alumnos - aprobados
    porcentaje_de_aprobados = 0
    
    if total_alumnos > 0:
        porcentaje_de_aprobados = round((aprobados / total_alumnos) * 100)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    story.append(Paragraph("<b>ACADEMIQ - REPORTE DE RENDIMIENTO CONSOLIDADO</b>", styles['Heading1']))
    story.append(Paragraph(f"Curso ID: {idCurso} | Vista de Calificaciones Finales Estimadas", styles['Normal']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(f"<b>Alumnos Evaluados:</b> {total_alumnos}", styles['Normal']))
    story.append(Paragraph(f"<b>Alumnos que Promocionan/Aprueban (Nota >= 4.0):</b> {aprobados}", styles['Normal']))
    story.append(Paragraph(f"<b>Alumnos con Cursada Desaprobada (Nota < 4.0):</b> {desaprobados}", styles['Normal']))
    story.append(Paragraph(f"<b>Porcentaje General de Aprobación de la Comisión:</b> {porcentaje_de_aprobados}%", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if total_alumnos > 0:
        tabla_datos = [["Padrón", "Nombre y Apellido", "Promedio Individual", "Condición Cursada"]]
        
        for fila in alumnos_promedios:
            promedio_num = round(float(fila['promedio_final']), 2)
            estado_texto = "Aprobado" if promedio_num >= 4.0 else "Desaprobado"
            tabla_datos.append([
                str(fila['padron']),
                fila['nombres'],
                str(promedio_num),
                estado_texto
            ])
            
        tabla_pdf = Table(tabla_datos, colWidths=[80, 240, 100, 100])
        tabla_pdf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2d5986")), 
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(tabla_pdf)
    else:
        story.append(Paragraph("<i>No se encontraron registros de notas para generar el listado.</i>", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=f'rendimiento_general_curso_{idCurso}.pdf'
    )

#--------------------------------------------------------------------------------------------------------
# GET /api/cursos
# Lista todos los cursos asignados al profesor logueado
#--------------------------------------------------------------------------------------------------------
@cursos_bp.route('', methods=['GET'])
def get_cursos():

    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT c.idCurso, c.nombre, c.codigo, c.cuatrimestre, c.descripcion 
            FROM Curso c
            INNER JOIN Curso_has_Usuarios chu ON c.idCurso = chu.Curso_idCurso
            WHERE chu.Usuarios_padron = %s
        """
        cursor.execute(query, (padron_operador,))
        cursos = cursor.fetchall()
        
        return jsonify({"cursos": cursos}), 200
        
    except Exception as e:
        return errors.server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# POST /api/cursos
# Permite a un profesor crear un nuevo curso en el sistema (con validaciones de unicidad)
#--------------------------------------------------------------------------------------------------------
@cursos_bp.route('', methods=['POST'])
def create_curso():
        
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])

    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos para agregar alumnos o token inválido")
    
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    data = request.get_json(silent=True) or {}
    
    if not data:
        return errors.bad_request("No se recibió un cuerpo JSON válido en la solicitud.")

    nombre = str(data.get("nombre")).strip()
    codigo = (data.get("codigo")).strip()
    cuatrimestre = str(data.get("cuatrimestre")).strip()
    descripcion = str(data.get("descripcion", "")).strip()


    error_formato = validaciones.validar_curso_datos(nombre, codigo)
    if error_formato:
        return error_formato

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        

        error_unicidad = validaciones.verificar_unicidad_curso(cursor, nombre, codigo)
        if error_unicidad:
            return jsonify(error_unicidad), 409
            

        query_insert = """
            INSERT INTO Curso (nombre, codigo, cuatrimestre, descripcion, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query_insert, (nombre, codigo, cuatrimestre, descripcion))
        id_curso = cursor.lastrowid
        

        query_relacion = """
            INSERT INTO Curso_has_Usuarios (Curso_idCurso, Usuarios_padron)
            VALUES (%s, %s)
        """
        cursor.execute(query_relacion, (id_curso, padron_operador))
        
        funciones.registrar_auditoria(cursor, padron_operador, f"Creó el curso {nombre} ({codigo})")
        conn.commit()
        
        return errors.well_response(f"Curso '{nombre}' creado exitosamente con ID {id_curso}")
        
    except Exception as e:
        if conn: conn.rollback()
        return errors.server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# DELETE /api/cursos/{idCurso}
# Permite eliminar un curso determinado
#--------------------------------------------------------------------------------------------------------
@cursos_bp.route('/<int:idCurso>', methods=['DELETE'])
def delete_curso(idCurso):
    
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM Curso WHERE idCurso = %s"
        cursor.execute(query, (idCurso,))
        
        if cursor.rowcount == 0:
            return errors.not_found(f"No se encontró el curso con ID {idCurso}")
            
        funciones.registrar_auditoria(cursor, padron_operador, f"Eliminó el curso con ID {idCurso}")
        conn.commit()
        
        return errors.ok_response(f"Curso con ID {idCurso} eliminado de forma permanente")
        
    except Exception as e:
        if conn: conn.rollback()
        return errors.server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

#--------------------------------------------------------------------------------------------------------
# PATCH /api/cursos/{idCurso}
# Permite cambiar campos de un curso de manera parcial
#--------------------------------------------------------------------------------------------------------
@cursos_bp.route('/<int:idCurso>', methods=['PATCH'])
def patch_curso(idCurso):
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)

    data = request.get_json(silent=True) or {}
    
    if not data:
        return errors.bad_request("Debe enviar campos para actualizar.")
        
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        

        cursor.execute("SELECT nombre, codigo FROM Curso WHERE idCurso = %s", (idCurso,))
        curso_actual = cursor.fetchone()
        if not curso_actual:
            return errors.not_found(f"No existe el curso con ID {idCurso}")
            

        nuevo_nombre = data.get("nombre", curso_actual["nombre"]).strip()
        nuevo_codigo = data.get("codigo", curso_actual["codigo"]).strip()
        
        error_formato = validaciones.validar_curso_datos(nuevo_nombre, nuevo_codigo)
        if error_formato:
            return error_formato
            
        error_unicidad = validaciones.verificar_unicidad_curso(cursor, nuevo_nombre, nuevo_codigo, id_curso_ignorar=idCurso)
        if error_unicidad:
            return jsonify(error_unicidad), 409
            

        updates = []
        params = []
        for key in ["nombre", "codigo", "cuatrimestre", "descripcion"]:
            if key in data:
                updates.append(f"{key} = %s")
                params.append(str(data[key]).strip())
                
        if not updates:
            return errors.bad_request("Ninguno de los campos enviados es modificable.")
            
        query_update = f"UPDATE Curso SET {', '.join(updates)} WHERE idCurso = %s"
        params.append(idCurso)
        
        cursor.execute(query_update, tuple(params))
        funciones.registrar_auditoria(cursor, padron_operador, f"Modificó parcialmente el curso {idCurso}")
        conn.commit()
        
        return errors.ok_response(f"Curso {idCurso} modificado de forma exitosa")
        
    except Exception as e:
        if conn: conn.rollback()
        return errors.server_error(str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



@cursos_bp.route('/<int:idCurso>/evaluaciones', methods=['POST'])
def create_evaluacion(idCurso): # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    data = request.get_json()
    

    tipo = data.get('tipo')
    descripcion = data.get('descripcion')
    fecha = data.get('fecha')

    curso_id = idCurso if idCurso else data.get('Curso_idCurso')


    if not all([tipo, descripcion, fecha, curso_id]):
        return jsonify({'error': 'Faltan campos requeridos: tipo, descripcion, fecha, curso_id'}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT idCurso FROM Curso WHERE idCurso = %s", (curso_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Curso no encontrado'}), 404

        cursor.execute(
            "INSERT INTO Evaluaciones (tipo, descripcion, fecha, Curso_idCurso) VALUES (%s, %s, %s, %s)",
            (tipo, descripcion, fecha, curso_id)
        )
        conn.commit()
        
        idEvaluacion = cursor.lastrowid

        return jsonify({
            'message': 'Evaluación creada exitosamente',
            'idEvaluacion': idEvaluacion
        }), 201

    except IntegrityError as e:
        return jsonify({'error': 'Error de integridad: {}'.format(str(e))}), 400
    except Exception as e:
        return jsonify({'error': 'Error al crear la evaluación: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@cursos_bp.route('/<int:idCurso>/evaluaciones', methods=['GET'])
def get_evaluaciones(idCurso):  # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Evaluaciones WHERE Curso_idCurso = %s", (idCurso,))
        evaluaciones = cursor.fetchall()

        return jsonify(evaluaciones), 200

    except Exception as e:
        return jsonify({'error': 'Error al obtener evaluaciones: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@cursos_bp.route('/<int:idCurso>/evaluaciones/<int:idEvaluacion>', methods=['GET'])
def get_evaluacion(idCurso, idEvaluacion):  # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Evaluaciones WHERE idEvaluacion = %s AND Curso_idCurso = %s", (idEvaluacion, idCurso))
        evaluacion = cursor.fetchone()

        if evaluacion is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404

        return jsonify(evaluacion), 200

    except Exception as e:
        return jsonify({'error': 'Error al obtener la evaluación: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@cursos_bp.route('/<int:idCurso>/evaluaciones/<int:idEvaluacion>', methods=['PUT'])
def update_evaluacion(idCurso, idEvaluacion):  # Agregado idCurso por la herencia
    tiene_acceso = funciones.evaluar_acceso_seguro(request.headers, ["Docente"])
    
    if not tiene_acceso:
        return errors.acceso_denegado1("No tiene permisos o token inválido")
        
    padron_operador = funciones.obtener_padron_desde_headers(request.headers)
    
    conn = None
    cursor = None

    data = request.get_json()
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Evaluaciones WHERE idEvaluacion = %s AND Curso_idCurso = %s", (idEvaluacion, idCurso))
        evaluacion_actual = cursor.fetchone()
        
        if evaluacion_actual is None:
            return jsonify({'error': 'Evaluación no encontrada'}), 404
        
        # Usar valores actuales si no se proporcionan nuevos
        tipo = data.get('tipo', evaluacion_actual['tipo'])
        descripcion = data.get('descripcion', evaluacion_actual['descripcion'])
        fecha = data.get('fecha', evaluacion_actual['fecha'])
        curso_id = idCurso
        
        cursor.execute(
            """UPDATE Evaluaciones 
               SET tipo = %s, descripcion = %s, fecha = %s, Curso_idCurso = %s 
               WHERE idEvaluacion = %s AND Curso_idCurso = %s""",
            (tipo, descripcion, fecha, curso_id, idEvaluacion, idCurso)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM Evaluaciones WHERE idEvaluacion = %s", (idEvaluacion,))
        evaluacion_actualizada = cursor.fetchone()
        
        return jsonify({
            'message': 'Evaluación actualizada exitosamente',
            'evaluacion': evaluacion_actualizada
        }), 200

    except Exception as e:
        return jsonify({'error': 'Error al actualizar la evaluación: {}'.format(str(e))}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
