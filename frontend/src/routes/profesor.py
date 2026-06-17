from flask import Blueprint, jsonify, render_template, request, redirect, flash, session, url_for, Response
from backend.src.db.db import get_connection
from src.utils import utils as utils
from src.services import cursos as api_cursos
from src.services import alumnos as api_alumnos
from src.services import evaluaciones as api_evaluaciones
from src.services import ev_notas_service as api_notas
from src.services import equipos as api_equipos

profesor_bp = Blueprint('profesor', __name__)




@profesor_bp.route('/asistencia', methods = ['GET'])
def asistencia():
    return render_template('profesor-asistencia.html')
#---------------------------------------------------------------------------------------------------------

# VISTA GENERAL DOCENTE

#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/dashboard', methods=['GET'])
def dashboard():
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder al panel.", "error")
        return redirect(url_for('auth.login'))
        
    resultado = api_cursos.obtener_cursos(usuario['token'])
    cursos_lista = resultado.get('cursos', []) if resultado.get('ok') else []
    
    return render_template('profesor-dashboard.html', cursos=cursos_lista)

#-------------------------------------------------------------------------------------------------------
@profesor_bp.route('/curso/<int:id_curso>/exportar_alumnos_pdf', methods=['GET'])
def exportar_alumnos_pdf(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder a esta función.", "error")
        return redirect(url_for('auth.login'))
        
    ordenar_por = request.args.get('ordenar_por', 'apellido')
    filtrar_activos = request.args.get('filtrar_activos', 'todos')
    
    response_api = api_alumnos.descargar_reporte_alumnos_pdf(
        token=usuario['token'],
        id_curso=id_curso,
        ordenar_por=ordenar_por,
        filtrar_activos=filtrar_activos
    )
    
    if not response_api or response_api.status_code != 200:
        flash("No se pudo generar el reporte de alumnos en formato PDF.", "error")
        return redirect(url_for('profesor.dashboard'))
        
    return Response(
        response_api.content,
        headers={
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename=alumnos_curso_{id_curso}.pdf'
        }
    )
#---------------------------------------------------------------------------------------------------------

# MODULO DE GESTIÓN DE CURSOS (COMISIONES)

#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos', methods=['GET'])
def vista_cursos():
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder a tus cursos.", "error")
        return redirect(url_for('auth.login'))
        
    # GET /api/cursos
    resultado = api_cursos.obtener_cursos(usuario['token'])
    cursos_lista = resultado.get('cursos', []) if resultado.get('ok') else []
    
    return render_template('profesor-cursos.html', cursos=cursos_lista)
#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/crear', methods=['POST'])
def crear_curso():
    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))
    
    nombre = request.form.get('nombre', '').strip()
    codigo = request.form.get('codigo', '').strip()
    cuatrimestre = request.form.get('cuatrimestre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    
    # POST /api/cursos
    resultado = api_cursos.crear_curso(usuario['token'], nombre, codigo, cuatrimestre, descripcion)
    
    if resultado.get('ok'):
        flash("Curso creado exitosamente.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.vista_cursos'))
#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/actualizar/<int:id_curso>', methods=['POST'])
def actualizar_curso(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))
    
    nombre = request.form.get('nombre', '').strip()
    codigo = request.form.get('codigo', '').strip()
    cuatrimestre = request.form.get('cuatrimestre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    
    # PATCH /api/cursos/{idCurso}
    resultado = api_cursos.actualizar_curso(usuario['token'], id_curso, nombre, codigo, cuatrimestre, descripcion)
    
    if resultado.get('ok'):
        flash("Comisión modificada correctamente.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.vista_cursos'))
#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/eliminar/<int:id_curso>', methods=['POST'])
def eliminar_curso(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))
    
    # DELETE /api/cursos/{idCurso}
    resultado = api_cursos.eliminar_curso(usuario['token'], id_curso)
    
    if resultado.get('ok'):
        flash("Curso eliminado permanentemente.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.vista_cursos'))
#---------------------------------------------------------------------------------------------------------

# GESTIÓN DE ALUMNOS

#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:id_curso>/alumnos/inscribir', methods=['POST'])
def inscribir_alumno(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))
    
    padron = request.form.get('padron', '').strip()
    nombres = request.form.get('nombres', '').strip()
    mail = request.form.get('mail', '').strip()
    
    # POST /api/cursos/{curso-id}/alumnos
    resultado = api_alumnos.agregar_alumno(usuario['token'], id_curso, padron, nombres, mail)
    
    if resultado.get('ok'):
        flash("Alumno agregado correctamente al curso.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.vista_alumnos', id_curso=id_curso))
#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:id_curso>/alumnos/importar', methods=['POST'])
def importar_csv(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))
    
    file = request.files.get('file')
    if not file or file.filename == '':
        flash("No seleccionaste ningún archivo CSV.", "error")
        return redirect(url_for('profesor.vista_alumnos', id_curso=id_curso))
        
    # POST /api/cursos/{curso-id}/alumnos/importar
    resultado = api_alumnos.importar_csv(usuario['token'], id_curso, file)
    
    if resultado.get('ok'):
        flash("Importación masiva completada con éxito.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.vista_alumnos', id_curso=id_curso))
#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:id_curso>/alumnos/baja-logica/<int:padron>', methods=['POST'])
def baja_logica_alumno(id_curso, padron):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))
    
    # DELETE /api/cursos/{idCurso}/alumnos/{padron} 
    resultado = api_alumnos.baja_logica_alumno(usuario['token'], id_curso, padron)
    
    if resultado.get('ok'):
        flash(f"Baja lógica procesada con éxito para el alumno {padron}.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.vista_alumnos', id_curso=id_curso))
#---------------------------------------------------------------------------------------------------------
@profesor_bp.route('/cursos/<int:id_curso>/alumnos/ficha/<int:padron>', methods=['GET'])
def vista_ficha_alumno(id_curso, padron):

    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))

    resultado = api_alumnos.obtener_alumno_por_padron(usuario['token'], id_curso, padron)

    if resultado.get('ok'):
        alumno_data = resultado.get('alumno', {})
        curso_mock = {"idCurso": id_curso}

        return render_template('profesor-alumno-ficha.html', curso=curso_mock, alumno=alumno_data)

    for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
        flash(mensaje, 'error')
        
    return redirect(url_for('profesor.vista_alumnos', id_curso=id_curso))

#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:id_curso>/alumnos', methods=['GET'])
def vista_alumnos(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return redirect(url_for('auth.login'))
        
    padron_buscar = request.args.get('buscar', '').strip()
    estado_filtro = request.args.get('estado')
    if estado_filtro == "": 
        estado_filtro = None

    if padron_buscar.isdigit():
        resultado = api_alumnos.obtener_alumno_por_padron(usuario['token'], id_curso, int(padron_buscar))
        
        if resultado.get('ok') and resultado.get('alumno'):
            alumno = resultado['alumno']
            alumnos_lista = [{
                "nombres": alumno.get("nombres"),
                "padron": alumno.get("padron"),
                "mail": alumno.get("mail"),
                "Estado": alumno.get("Estado")
            }]
        else:
            alumnos_lista = []
            flash(f"No se encontró ningún alumno con el padrón {padron_buscar}.", "error")
            
    else:
        resultado = api_alumnos.obtener_alumnos(usuario['token'], id_curso, estado_filtro)
        alumnos_lista = resultado.get('alumnos', []) if resultado.get('ok') else []
    
    curso_mock = {"idCurso": id_curso}
    return render_template('profesor-alumnos.html', curso=curso_mock, alumnos=alumnos_lista)
#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:id_curso>/alumnos/actualizar/<int:padron>', methods=['POST'])
def actualizar_alumno(id_curso, padron):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: return redirect(url_for('auth.login'))
    
    nombres = request.form.get('nombres', '').strip()
    mail = request.form.get('mail', '').strip()
    estado = request.form.get('estado') 
    
    # PATCH /api/cursos/<idCurso>/alumnos/<padron>
    resultado = api_alumnos.actualizar_alumno(usuario['token'], id_curso, padron, nombres, mail, estado)
    
    if resultado.get('ok'):
        flash("Datos del alumno modificados correctamente.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.vista_alumnos', id_curso=id_curso))
#---------------------------------------------------------------------------------------------------------


# GESTIÓN DE EVALUACIONES
#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones', methods=['GET', 'POST'])
def evaluaciones(curso_id):
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder al panel.", "error")
        return redirect(url_for('auth.login'))
    
    token = usuario.get('token')
    session['curso_actual'] = curso_id

    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form.get('fecha', '').strip()
        
        if not tipo or not descripcion or not fecha:
            flash("Todos los campos son obligatorios", "error")
            return redirect(url_for('profesor.evaluaciones', curso_id=curso_id))
        
        resultado = api_evaluaciones.crear_evaluacion(token, tipo, descripcion, fecha, curso_id)
        
        if resultado.get('ok'):
            flash(resultado.get('message', 'Evaluación creada exitosamente'), 'success')
        else:
            errores = resultado.get('error_response', {}).get('errors', [])
            for e in errores:
                flash(e.get('description', 'Error al crear evaluación'), 'error')
        
        return redirect(url_for('profesor.evaluaciones', curso_id=curso_id))
    
    # GET: obtener evaluaciones
    resultado = api_evaluaciones.obtener_evaluaciones(token, curso_id=curso_id)
    
    evaluaciones_lista = []
    if resultado.get('ok'):
        evaluaciones_lista = resultado.get('evaluaciones', [])
    else:
        errores = resultado.get('error_response', {}).get('errors', [])
        for e in errores:
            flash(e.get('description', 'Error al obtener evaluaciones'), 'error')
    
    # Obtener información del curso actual
    cursos_resultado = api_cursos.obtener_cursos(token)
    cursos = cursos_resultado.get('cursos', []) if cursos_resultado.get('ok') else []
    curso_actual = next((c for c in cursos if c.get('idCurso') == curso_id), {'idCurso': curso_id, 'nombre': f'Curso {curso_id}'})
    
    return render_template('profesor-evaluaciones.html', 
                         evaluaciones=evaluaciones_lista,
                         cursos=cursos,
                         curso=curso_actual, 
                         curso_id=curso_id)

#-----------------------------------------------------------------------------------------------------
@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones/<int:id>', methods=['GET'])
def api_get_evaluacion(curso_id, id): 
    """API para obtener una evaluación específica (para editar)"""
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return jsonify({'error': 'No autorizado'}), 401
    
    token = usuario.get('token')
    resultado = api_evaluaciones.obtener_evaluacion(token, id)
    
    if resultado.get('ok'):
        evaluaciones = resultado.get('evaluaciones', [])
        if isinstance(evaluaciones, list) and len(evaluaciones) > 0:
            evaluacion = evaluaciones[0]
        elif isinstance(evaluaciones, dict):
            evaluacion = evaluaciones
        else:
            evaluacion = None
        
        if evaluacion:
            return jsonify(evaluacion)
    
    return jsonify({'error': 'Evaluación no encontrada'}), 404

#----------------------------------------------------------------------------------------------------
@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones/actualizar/<int:idEvaluacion>', methods=['POST'])
def actualizar_evaluacion_route(curso_id, idEvaluacion):

    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder al panel.", "error")
        return redirect(url_for('auth.login'))
    
    token = usuario.get('token')
    
    tipo = request.form.get('tipo', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    fecha = request.form.get('fecha', '').strip()
    
    resultado = api_evaluaciones.actualizar_evaluacion(
        token, 
        idEvaluacion,
        tipo=tipo if tipo else None,
        descripcion=descripcion if descripcion else None,
        fecha=fecha if fecha else None,
        curso_id=int(curso_id)
    )
    
    if resultado.get('ok'):
        flash('✅ Evaluación actualizada exitosamente', 'success')
    else:
        errores_lista = resultado.get('error_response', {}).get('errors', [])
        for e in errores_lista:
            flash(f'❌ Error: {e.get("description", "Error al actualizar")}', 'error')
    
    return redirect(url_for('profesor.evaluaciones', curso_id=curso_id))
#----------------------------------------------------------------------------------------------------


# GESTIÓN DE NOTAS
#----------------------------------------------------------------------------------------------------
@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones/notas/ver', methods=['GET'])
def ver_nota(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))


    id_ev = request.args.get('id_ev', type=int)
    tipo = request.args.get('tipo')
    id_g = request.args.get('id_g')

    curso = {"idCurso": curso_id} if curso_id else None
    # Si se ingresa por el template de "profesor-evaluaciones" (con curso_id y id_ev)
    if not all([curso_id, id_ev, id_g, tipo]):
        return render_template('ver_nota.html', 
                               nota=None, 
                               error=None, 
                               curso_id=curso_id, 
                               id_evaluaciones=id_ev,
                               curso=curso)


    if not curso_id and not id_ev and not id_g and not tipo:
        return render_template('ver_nota.html', nota=None, error=None)

    resultado = api_notas.consultar_nota(curso_id, id_ev, id_g, tipo)

    if resultado["codigo"] == 200:
        return render_template('ver_nota.html', 
                               nota=resultado["datos"], 
                               error=None,
                               curso_id=curso_id, 
                               id_evaluaciones=id_ev, 
                               id_g=id_g, 
                               tipo=tipo,
                               curso=curso)
    else:
        return render_template('ver_nota.html', nota=None, error=resultado["error"], curso_id=curso_id, id_evaluaciones=id_ev, id_g=id_g, tipo=tipo, curso=curso)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones/notas/cargar', methods=['GET', 'POST'])
def procesar_guardado(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))

    curso = {"idCurso": curso_id} if curso_id else None

    id_evaluacion = request.form.get('id_evaluacion', type=int)
    id_g = request.form.get('id_g')
    nota = request.form.get('nota')
    tipo = request.form.get('tipo')

    if request.method == 'POST':

        resultado = api_notas.cargar_nota(curso_id, id_evaluacion, id_g, nota, tipo)

        if resultado["codigo"] in [200, 201]:
            # Determino un nuevo valor para 'estado'.
            return redirect(url_for('profesor.procesar_guardado',curso_id=curso_id, estado='ok'))
        else:
            return render_template('manejo_de_error.html', error_msg=resultado['error']), resultado["codigo"]

    id_evaluacion = request.args.get('id_evaluaciones')

    estado = request.args.get('estado')
    return render_template('cargar_nota.html', estado=estado, curso=curso, curso_id=curso_id, id_evaluacion=id_evaluacion)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:curso_id>/evaluaciones/notas/editar', methods=['GET', 'POST'])
def procesar_actualizacion(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))

    if request.method == 'POST': 

        id_ev = request.form.get('id_ev')
        id_g = request.form.get('id_g')    
        nota_nueva = request.form.get('nota')
        tipo = request.form.get('tipo')

        resultado = api_notas.actualizar_nota(curso_id, id_ev, id_g, nota_nueva, tipo)

        if resultado["codigo"] == 200:
            return redirect(f"/profesor/cursos/{curso_id}/evaluaciones/notas/ver?&id_ev={id_ev}&id_g={id_g}&tipo={tipo}")
    
    query_params = {
        'curso_id': curso_id, 
        'id_ev': request.args.get('id_ev'), 
        'id_g': request.args.get('id_g'), 
        'tipo': request.args.get('tipo')
    }
    return render_template('editar_nota.html', **query_params)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------


#GESTIÓN DE EQUIPOS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
@profesor_bp.route('/cursos/<int:curso_id>/equipos/alumnos', methods=['GET'])
def ver_equipos(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))

    try:
        curso_id = utils.validar_curso_id(curso_id)
    except ValueError as error:
        return str(error), 400

    equipos = api_equipos.listar_equipos(curso_id)
    return render_template("profesor-equipos.html",curso_id=curso_id,teams=equipos)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:curso_id>/equipos/alumnos/alta', methods=['POST'])
def agregar_miembro(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return redirect(url_for('auth.login'))

    try:
        curso_id = utils.validar_curso_id(curso_id)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    padron = request.form.get("nuevo_padron")
    equipo_id = request.form.get("equipo_id")

    try:
        padron = utils.validar_padron(padron)
        equipo_id = utils.validar_equipo_id(equipo_id)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    body = {"alumno_padron": int(padron),
            "equipo_id": int(equipo_id),
            "activo": 1}

    try:
        api_equipos.actualizar_equipo(curso_id, padron, body)
        flash("Integrante agregado correctamente.", "success")
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:curso_id>/equipos/alumnos/baja', methods=['POST'])
def eliminar_miembro(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return redirect(url_for('auth.login'))

    try:
        curso_id = utils.validar_curso_id(curso_id)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    padron = request.form.get('padron')
    equipo_id = request.form.get("equipo_id")

    try:
        padron = utils.validar_padron(padron)
        equipo_id = utils.validar_equipo_id(equipo_id)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    body = {"alumno_padron": int(padron),
            "equipo_id": int(equipo_id),
            "activo": 0}

    try:
        api_equipos.actualizar_equipo(curso_id, padron, body)
        flash("Integrante removido correctamente.", "success")
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:curso_id>/equipos/alumnos/delete', methods=['POST'])
def disolver_equipo(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return redirect(url_for('auth.login'))

    try:
        curso_id = utils.validar_curso_id(curso_id)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    padron = request.form.get('padron')

    try:
        padron = utils.validar_padron(padron)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    try:
        api_equipos.eliminar_equipo(curso_id, padron)
        flash("Equipo disuelto correctamente.", "success")
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos/<int:curso_id>/equipos/alumnos/agregar', methods=['POST'])
def agregar_equipo(curso_id):

    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        return redirect(url_for('auth.login'))

    try:
        curso_id = utils.validar_curso_id(curso_id)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    nombre = request.form.get("nombre")
    cupo = request.form.get("cupo")
    padrones_raw = request.form.get("padrones")

    try:
        if not nombre:
            raise ValueError("El nombre del equipo es obligatorio")

        if not padrones_raw:
            raise ValueError("Debe ingresar al menos un padrón")

        padrones = [utils.validar_padron(p.strip()) for p in padrones_raw.split(",")if p.strip()]

        if len(padrones) == 0:
            raise ValueError("No hay padrones válidos")

        body = {"nombre": nombre,
                "padrones": padrones,
                "cupo": int(cupo) if cupo else None}

    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))

    try:
        api_equipos.crear_equipo(curso_id, body)
        flash("Equipo creado correctamente.", "success")
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for('profesor.ver_equipos', curso_id=curso_id))