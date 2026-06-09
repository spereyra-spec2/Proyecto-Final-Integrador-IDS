from flask import Blueprint, render_template, request, redirect, flash, url_for
from src.utils import utils as utils
from src.services import cursos as api_cursos
from src.services import alumnos as api_alumnos

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
        
    # GET /api/cursos para rellenar las métricas y tablas del dashboard
    resultado = api_cursos.obtener_cursos(usuario['token'])
    cursos_lista = resultado.get('cursos', []) if resultado.get('ok') else []
    
    return render_template('profesor-dashboard.html', cursos=cursos_lista)
#---------------------------------------------------------------------------------------------------------

# MODULO DE GESTIÓN DE CURSOS (COMISIONES)

#---------------------------------------------------------------------------------------------------------

@profesor_bp.route('/cursos', methods=['GET'])
def vista_cursos():
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
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
    if not usuario: return redirect(url_for('auth.login'))
    
    # Utiliza la ruta GET /api/cursos/<idCurso>/alumnos/<padron> para extraer la ficha, notas y asistencias
    resultado = api_alumnos.obtener_ficha_alumno(usuario['token'], id_curso, padron)
    
    if resultado.get('ok'):
        alumno_data = resultado.get('alumno', {})
        curso_mock = {"idCurso": id_curso}
        # Debes tener una plantilla 'profesor-alumno-ficha.html' o similar para desplegar este objeto extendido
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
