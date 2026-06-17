from flask import Blueprint, flash, redirect, render_template, request, url_for
from src.services import cursos as cursos_service  # ← Cambiar alias para evitar conflicto
from .evaluaciones import evaluaciones_bp
from src.utils import utils


cursos_bp = Blueprint('cursos', __name__, url_prefix='/cursos')

# Registrar el blueprint de evaluaciones dentro de cursos
cursos_bp.register_blueprint(evaluaciones_bp)


#---------------------------------------------------------------------------------------------------------

@cursos_bp.route('', methods=['GET'])
def vista_cursos():
    usuario = utils.verificar_docente_autenticado()
    if not usuario:
        flash("Por favor, iniciá sesión para acceder a tus cursos.", "error")
        return redirect(url_for('auth.login'))
        
    # GET /api/cursos
    resultado = cursos_service.obtener_cursos_del_profesor(usuario['token'])  # ← Usar función correcta
    cursos_lista = resultado.get('cursos', []) if resultado.get('ok') else []
    
    return render_template('profesor-cursos.html', cursos=cursos_lista)

#---------------------------------------------------------------------------------------------------------

@cursos_bp.route('/crear', methods=['POST'])
def crear_curso():
    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))
    
    nombre = request.form.get('nombre', '').strip()
    codigo = request.form.get('codigo', '').strip()
    cuatrimestre = request.form.get('cuatrimestre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    
    # POST /api/cursos
    resultado = cursos_service.crear_curso(usuario['token'], nombre, codigo, cuatrimestre, descripcion)
    
    if resultado.get('ok'):
        flash("Curso creado exitosamente.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.cursos.vista_cursos'))

#---------------------------------------------------------------------------------------------------------

@cursos_bp.route('/actualizar/<int:id_curso>', methods=['POST'])
def actualizar_curso(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))
    
    nombre = request.form.get('nombre', '').strip()
    codigo = request.form.get('codigo', '').strip()
    cuatrimestre = request.form.get('cuatrimestre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    
    # PATCH /api/cursos/{idCurso}
    resultado = cursos_service.actualizar_curso(usuario['token'], id_curso, nombre, codigo, cuatrimestre, descripcion)
    
    if resultado.get('ok'):
        flash("Comisión modificada correctamente.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.cursos.vista_cursos'))

#---------------------------------------------------------------------------------------------------------

@cursos_bp.route('/eliminar/<int:id_curso>', methods=['POST'])
def eliminar_curso(id_curso):
    usuario = utils.verificar_docente_autenticado()
    if not usuario: 
        return redirect(url_for('auth.login'))
    
    # DELETE /api/cursos/{idCurso}
    resultado = cursos_service.eliminar_curso(usuario['token'], id_curso)
    
    if resultado.get('ok'):
        flash("Curso eliminado permanentemente.", "success")
    else:
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
            
    return redirect(url_for('profesor.cursos.vista_cursos'))