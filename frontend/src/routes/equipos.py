from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from backend.src.db.db import get_connection
from flask import jsonify
from frontend.src.services.equipos import listar_equipos, crear_equipo, actualizar_equipo, encontrar_equipos_del_alumno_activo, filtrar_equipos_por_nombre_y_codigo
from src.utils import utils as utils

equipos_bp = Blueprint('equipos', __name__)


@equipos_bp.route('/grupos', methods=['GET'])
def alumno_equipos():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT idCurso, nombre FROM Curso")
    cursos = cursor.fetchall()

    padron = request.args.get('padron')
    curso_id = request.args.get('curso_id')

    equipos_del_alumno = []
    busqueda_realizada = False

    try:
        curso_id = utils.validar_curso_id(curso_id)
        padron = utils.validar_padron(padron)
    except ValueError as error:
        return str(error), 400

    if padron and curso_id:
        busqueda_realizada = True

        try:
            todos_los_equipos = listar_equipos(curso_id) or []
            equipos_del_alumno = encontrar_equipos_del_alumno_activo(todos_los_equipos, padron)

        except Exception:
            equipos_del_alumno = []

    cursor.close()
    conn.close()

    return render_template('alumno-equipos.html', cursos = cursos, padron = padron, curso_id = curso_id, 
                           equipos_del_alumno = equipos_del_alumno, busqueda_realizada = busqueda_realizada)
                           


    
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@equipos_bp.route('/grupo_baja', methods=['POST'])
def alumno_leave():

    curso_id = request.form.get('curso_id')
    padron = request.form.get('padron')
    equipo_id = request.form.get('equipo_id')

    if not curso_id or not padron or not equipo_id:
        return "Faltan datos", 400

    try:
        curso_id = utils.validar_curso_id(curso_id)
        padron = utils.validar_padron(padron)
        equipo_id = utils.validar_equipo_id(equipo_id)
    except ValueError as error:
        return str(error), 400

    body = {"alumno_padron": int(padron),
            "activo": 0,
            "equipo_id": int(equipo_id)}

        
    actualizar_equipo(curso_id, padron, body)

    return redirect(url_for('equipos.alumno_equipos', padron=padron, curso_id=curso_id))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@equipos_bp.route('/grupo_crear', methods=['POST'])
def crear_nuevo_equipo():

    curso_id = request.form.get('curso_id')
    nombre_equipo = request.form.get('nombre_equipo')
    padrones = request.form.getlist('padrones[]')
    access_code = request.form.get('access_code')
    cupo = request.form.get('cupo')


    if not curso_id or not nombre_equipo or not padrones:
        return jsonify({"error": "Faltan datos obligatorios."}), 400

    try:
        body = {"nombre": nombre_equipo,
                "padrones": [int(p) for p in padrones],
                "access_code": access_code,
                "cupo": cupo}
        nuevo_equipo = crear_equipo(int(curso_id), body)

        return redirect(url_for('equipos.alumno_equipos', padron=padrones[0], curso_id=curso_id))

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {e}"}), 500
    
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@equipos_bp.route('/grupo_unirse', methods=['POST'])
def unirse_equipo():

    curso_id = request.form.get('curso_id')
    padron = request.form.get('padron')
    equipo_nombre = request.form.get('equipo_nombre')
    access_code = request.form.get('access_code')

    if not curso_id or not padron or not equipo_nombre:
        return jsonify({"error": "Faltan datos obligatorios."}), 400

    try:
        curso_id = utils.validar_curso_id(curso_id)
        padron = utils.validar_padron(padron)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    equipos = listar_equipos(curso_id) or []
    equipo_encontrado = filtrar_equipos_por_nombre_y_codigo(equipos, equipo_nombre, access_code)

    if not equipo_encontrado:
        return jsonify({"error": "Equipo inexistente o código incorrecto"}), 404

    equipo_id = equipo_encontrado["idEquipos"]

    body = {
        "alumno_padron": padron,
        "activo": 1,
        "equipo_id": equipo_id
    }

    actualizar_equipo(curso_id, padron, body)

    return redirect(url_for(
        'equipos.alumno_equipos',
        padron=padron,
        curso_id=curso_id
    ))