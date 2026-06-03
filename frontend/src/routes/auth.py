from flask import Blueprint, render_template, request, redirect, flash, url_for
from src import utils as utils
from src.services import auth as api

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    #si ya tiene sesión lo manda al inicio
    if utils.usuario_actual():
        return redirect(url_for('profesor.dashboard'))
    
    if request.method == 'POST':
        padron = request.form.get('padron', '').strip() #obtiene datos del json
        contrasena = request.form.get('contrasena', '')

        errores = []

        if not padron:
            errores.append("No ingresaste padrón")

        if not contrasena:
            errores.append("No ingresaste tu contraseña")

        if errores:
            for e in errores:
                flash(e, 'error')
            
            return render_template('login.html')
        try:
            padron = int(padron)
        except ValueError:
            flash("El padrón debe ser un número", "error")
            return render_template('login.html')


        resultado = api.login(int(padron), contrasena)

        if resultado.get('ok'):
            utils.guardar_sesion(resultado['token'], resultado['padron'], resultado['rol'])
            flash('Bienvenido', 'success')

            return redirect(url_for('profesor.dashboard'))
    
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')

        return render_template('login.html')
    
    return render_template('login.html') #si es get
