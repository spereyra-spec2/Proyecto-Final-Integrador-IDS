import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_cors import CORS
from src.routes.auth import auth_bp
from src.routes.profesor import profesor_bp
from src.routes.alumno import alumno_bp
from src.routes.ev_notas import notas_bp
from src.routes.evaluaciones import evaluaciones_bp

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

CORS(app)
app.config["JSON_SORT_KEYS"] = False
app.config['SECRET_KEY'] = 'clave_secreta_ids_2026'

app.register_blueprint(auth_bp, url_prefix="/auth") #sigo ejemplo del repo de cátedra
app.register_blueprint(profesor_bp, url_prefix="/profesor")
app.register_blueprint(alumno_bp, url_prefix="/alumno")
app.register_blueprint(notas_bp, url_prefix='/notas')
app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones" )

@app.route('/')
def index():
    return render_template('base_general.html')

@app.route('/alumno-inicio.html')
def alumno_inicio():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT idCurso AS id, nombre, codigo FROM Curso")
    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('alumno-inicio.html', cursos=cursos)



@app.route('/alumno-equipos.html', methods=['GET'])
def alumno_equipos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT idCurso, nombre FROM Curso")
    cursos = cursor.fetchall()

    padron = request.args.get('padron')
    curso_id = request.args.get('curso_id')

    equipos_del_alumno = []
    busqueda_realizada = False
    equipos_del_curso = []

    if padron and curso_id:
        busqueda_realizada = True
        try:
            from frontend.src.services.equipos import listar_equipos
            all_teams = listar_equipos(int(curso_id)) or []
            for t in all_teams:
                miembros = t.get('integrantes') or []
                for m in miembros:
                    p = m.get('padron') if isinstance(m, dict) else m
                    try:
                        if int(p) == int(padron):
                            equipos_del_alumno.append(t)
                            break
                    except Exception:
                        continue
        except Exception:
            equipos_del_alumno = []
        
    cursor.close()
    conn.close()

    teams = []
    try:
        if curso_id:
            from frontend.src.services.equipos import listar_equipos
            teams = listar_equipos(int(curso_id)) or []
    except Exception:
        teams = []

    return render_template(
        'alumno-equipos.html', 
        cursos=cursos,
        padron=padron,
        curso_id=int(curso_id) if curso_id else None,
        equipos_del_alumno=equipos_del_alumno,
        busqueda_realizada=busqueda_realizada,
        teams=teams,
    )


@app.route('/crear-equipo', methods=['POST'])
def crear_equipo_route():
    curso_id = request.form.get('curso_id')
    padron_creador = request.form.get('padron_creador')
    nombre_equipo = request.form.get('nombre_equipo', '').strip()

    if not curso_id or not nombre_equipo:
        flash('Faltan datos para crear el equipo', 'error')
        return redirect(url_for('alumno_equipos'))

    try:
        curso_id_int = int(curso_id)
    except Exception:
        flash('Curso inválido', 'error')
        return redirect(url_for('alumno_equipos'))

    try:
        conn_check = get_connection()
        cur_chk = conn_check.cursor()
        try:
            if padron_creador:
                cur_chk.execute("SELECT padron FROM Usuarios WHERE padron = %s", (int(padron_creador),))
                if cur_chk.fetchone() is None:
                    flash(f'El padrón {padron_creador} no existe en el sistema.', 'error')
                    return redirect(url_for('alumno_equipos', padron=padron_creador, curso_id=curso_id_int))
        finally:
            cur_chk.close(); conn_check.close()

        access_code = request.form.get('access_code')
        cupo_raw = request.form.get('cupo')
        cupo = None
        try:
            cupo = int(cupo_raw) if cupo_raw else None
        except Exception:
            cupo = None
        crear_equipo(curso_id_int, {'nombre': nombre_equipo, 'padrones': [int(padron_creador)] if padron_creador else [], 'access_code': access_code, 'cupo': cupo})
        flash('Equipo creado correctamente', 'success')
    except Exception as e:
        flash(f'Error creando equipo: {e}', 'error')

    return redirect(url_for('alumno_equipos', padron=padron_creador, curso_id=curso_id_int))


@app.route('/alumno-join', methods=['POST'])
def alumno_join():
    curso_id = request.form.get('curso_id')
    padron = request.form.get('padron')
    equipo_ref = request.form.get('equipo_ref')

    if not curso_id or not padron:
        flash('Faltan datos para unirse', 'error')
        return redirect(url_for('alumno_equipos'))

    try:
        curso_id_int = int(curso_id)
        padron_int = int(padron)
    except Exception:
        flash('Datos inválidos', 'error')
        return redirect(url_for('alumno_equipos'))

    if not equipo_ref:
        flash('No es posible unirse a un equipo vacío. Creá uno o pedí al docente que asigne integrantes.', 'error')
        return redirect(url_for('alumno_equipos', padron=padron_int, curso_id=curso_id_int))

    try:
        from frontend.src.services.equipos import actualizar_equipo
        res = actualizar_equipo(curso_id_int, int(equipo_ref), {"alumno_padron": padron_int, "activo": 1})
        if res is None:
            flash('No se pudo encontrar el equipo para unirse', 'error')
        else:
            flash('Te has unido al equipo', 'success')
    except Exception as e:
        flash(f'Error al unirse: {e}', 'error')

    return redirect(url_for('alumno_equipos', padron=padron_int, curso_id=curso_id_int))


@app.route('/alumno-join-by-code', methods=['POST'])
def alumno_join_by_code():
    curso_id = request.form.get('curso_id')
    padron = request.form.get('padron')
    access_code = request.form.get('access_code')
    equipo_nombre = request.form.get('equipo_nombre')

    if not curso_id or not padron or not access_code:
        flash('Faltan datos para unirse con código', 'error')
        return redirect(url_for('alumno_equipos'))

    try:
        curso_id_int = int(curso_id)
        padron_int = int(padron)
    except Exception:
        flash('Datos inválidos', 'error')
        return redirect(url_for('alumno_equipos'))

    try:
        from frontend.src.services.equipos import join_equipo_by_code
        res = join_equipo_by_code(curso_id_int, access_code.strip(), padron_int, equipo_nombre.strip() if equipo_nombre else None)
        flash('Solicitud de unión procesada correctamente', 'success')
    except Exception as e:
        flash(f'Error al unirse con código: {e}', 'error')

    return redirect(url_for('alumno_equipos', padron=padron_int, curso_id=curso_id_int))


@app.route('/alumno-leave', methods=['POST'])
def alumno_leave():
    curso_id = request.form.get('curso_id')
    padron = request.form.get('padron')

    if not curso_id or not padron:
        flash('Faltan datos para abandonar el equipo', 'error')
        return redirect(url_for('alumno_equipos'))

    try:
        curso_id_int = int(curso_id)
        padron_int = int(padron)
    except Exception:
        flash('Datos inválidos', 'error')
        return redirect(url_for('alumno_equipos'))

    try:
        from frontend.src.services.equipos import actualizar_equipo
        res = actualizar_equipo(curso_id_int, padron_int, {"alumno_padron": padron_int, "activo": 0})
        if res is None:
            flash('No se pudo abandonar el equipo (no encontrado)', 'error')
        else:
            flash('Abandonaste el equipo', 'success')
    except Exception as e:
        flash(f'Error al abandonar el equipo: {e}', 'error')

    return redirect(url_for('alumno_equipos', padron=padron_int, curso_id=curso_id_int))




@app.route('/login.html')
def login(): return render_template('login.html')

from frontend.src.services.equipos import listar_equipos, crear_equipo
import csv
import io
import requests


@app.route('/profesor-equipos.html', methods=['GET', 'POST'])
def profe_equipos():
    curso_id = request.args.get('curso') or request.form.get('curso_id')

    if not curso_id:
        flash('Falta parámetro curso', 'error')
        return render_template('profesor-equipos.html', teams=[], curso_id=None)

    try:
        curso_id_int = int(curso_id)
    except Exception:
        flash('Curso inválido', 'error')
        return render_template('profesor-equipos.html', teams=[], curso_id=None)

    if request.method == 'POST' and request.form.get('action') == 'create':
        nombre = request.form.get('nombre', '').strip()
        padrones_raw = request.form.get('padrones', '').strip()
        if not nombre:
            flash('El nombre del equipo es obligatorio', 'error')
            return redirect(url_for('profe_equipos', curso=curso_id_int))
        padrones_list = []
        if padrones_raw:
            try:
                padrones_list = [int(x.strip()) for x in padrones_raw.split(',') if x.strip()]
            except Exception:
                flash('Los padrónes iniciales deben ser números separados por comas', 'error')
                return redirect(url_for('profe_equipos', curso=curso_id_int))
            conn_chk = get_connection()
            cur_chk = conn_chk.cursor()
            try:
                missing = []
                for p in padrones_list:
                    cur_chk.execute("SELECT padron FROM Usuarios WHERE padron = %s", (p,))
                    if cur_chk.fetchone() is None:
                        missing.append(p)
                if missing:
                    flash(f"Los siguientes padrónes no existen: {', '.join(str(x) for x in missing)}", 'error')
                    return redirect(url_for('profe_equipos', curso=curso_id_int))
            finally:
                cur_chk.close(); conn_chk.close()
        try:
            access_code_prof = request.form.get('access_code')
            cupo_prof_raw = request.form.get('cupo')
            cupo_prof = None
            try:
                cupo_prof = int(cupo_prof_raw) if cupo_prof_raw else None
            except Exception:
                cupo_prof = None
            crear_equipo(curso_id_int, {'nombre': nombre, 'padrones': padrones_list, 'access_code': access_code_prof, 'cupo': cupo_prof})
            flash('Equipo creado', 'success')
        except Exception as e:
            flash(f'Error creando equipo: {e}', 'error')
        return redirect(url_for('profe_equipos', curso=curso_id_int))

    teams = []
    try:
        teams = listar_equipos(curso_id_int)
    except Exception as e:
        flash(f'No se pudo obtener equipos: {e}', 'error')

    return render_template('profesor-equipos.html', teams=teams, curso_id=curso_id_int)


@app.route('/profe-add-member', methods=['POST'])
def profe_add_member():
    curso_id = request.form.get('curso_id')
    equipo_ref = request.form.get('equipo_ref')
    nuevo_padron = request.form.get('nuevo_padron')

    if not curso_id or not equipo_ref or not nuevo_padron:
        flash('Faltan datos para agregar integrante', 'error')
        return redirect(url_for('profe_equipos', curso=curso_id))

    try:
        curso_id_int = int(curso_id)
        equipo_ref_int = int(equipo_ref)
        nuevo_padron_int = int(nuevo_padron)
    except Exception:
        flash('Datos inválidos', 'error')
        return redirect(url_for('profe_equipos', curso=curso_id))

    try:
        from frontend.src.services.equipos import actualizar_equipo
        body = {"alumno_padron": nuevo_padron_int, "activo": 1}
        res = actualizar_equipo(curso_id_int, equipo_ref_int, body)
        if res is None:
            flash('No se encontró el equipo para agregar integrante', 'error')
        else:
            flash('Integrante agregado correctamente', 'success')
    except Exception as e:
        flash(f'Error agregando integrante: {e}', 'error')

    return redirect(url_for('profe_equipos', curso=curso_id_int))


@app.route('/profe-remove-member', methods=['POST'])
def profe_remove_member():
    curso_id = request.form.get('curso_id')
    equipo_ref = request.form.get('equipo_ref')
    padron = request.form.get('padron')

    if not curso_id or not equipo_ref or not padron:
        flash('Faltan datos para remover integrante', 'error')
        return redirect(url_for('profe_equipos', curso=curso_id))

    try:
        curso_id_int = int(curso_id)
        equipo_ref_int = int(equipo_ref)
        padron_int = int(padron)
    except Exception:
        flash('Datos inválidos', 'error')
        return redirect(url_for('profe_equipos', curso=curso_id))

    try:
        from frontend.src.services.equipos import actualizar_equipo
        body = {"alumno_padron": padron_int, "activo": 0}
        res = actualizar_equipo(curso_id_int, equipo_ref_int, body)
        if res is None:
            flash('No se encontró el equipo o integrante', 'error')
        else:
            flash('Integrante removido correctamente', 'success')
    except Exception as e:
        flash(f'Error removiendo integrante: {e}', 'error')

    return redirect(url_for('profe_equipos', curso=curso_id_int))


@app.route('/importar-alumnos', methods=['POST'])
def importar_alumnos_front():
    file = request.files.get('file')
    curso_id = request.form.get('curso_id')
    if not file or not curso_id:
        flash('Archivo o curso faltante', 'error')
        return redirect(url_for('profesor_alumnos') if 'profesor_alumnos' in globals() else url_for('index'))

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
        reader = csv.DictReader(stream)
        required = {'padron', 'nombres', 'mail'}
        if not required.issubset(set(k.strip().lower() for k in reader.fieldnames or [])):
            flash('El CSV debe contener columnas: padron,nombres,mail', 'error')
            return redirect(request.referrer or url_for('index'))
    
        invalid = []
        rows = []
        for r in reader:
            pad = r.get('padron') or r.get('Padron') or r.get('PADRON')
            try:
                int(pad)
            except Exception:
                invalid.append(pad)
            rows.append(r)
        if invalid:
            flash(f'Padrónes inválidos en CSV: {invalid[:5]}', 'error')
            return redirect(request.referrer or url_for('index'))

        file.stream.seek(0)
        files = {'file': (file.filename, file.stream, file.mimetype)}
        backend_url = f'http://127.0.0.1:3006/api/cursos/{curso_id}/alumnos/importar'
        resp = requests.post(backend_url, files=files, timeout=30)
        if resp.status_code in (200,201):
            flash('Importación enviada al backend', 'success')
        else:
            flash(f'Error en importación: {resp.status_code} {resp.text[:200]}', 'error')
        return redirect(request.referrer or url_for('index'))
    except Exception as e:
        flash(f'Error procesando CSV: {e}', 'error')
        return redirect(request.referrer or url_for('index'))


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static', 'css'), filename)

@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static', 'js'), filename)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
