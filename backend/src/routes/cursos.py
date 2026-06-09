from flask import Blueprint, request, jsonify
from src.db.db import _get_connection
import src.utils.errors as errors
import src.utils.validaciones as validaciones
import src.utils.funciones as funciones

cursos_bp = Blueprint('cursos', __name__)

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
        conn = _get_connection()
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
        conn = _get_connection()
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
            INSERT INTO Curso_has_Usuarios (Curso_idCurso, Usuarios_padron, Estado)
            VALUES (%s, %s, 1)
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
        conn = _get_connection()
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
        conn = _get_connection()
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