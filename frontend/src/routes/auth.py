from flask import Blueprint, render_template, request, redirect, flash, url_for
from src import utils as utils
from src.services import auth as api

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':

        padron = request.form.get('padron', '').strip()
        nombre = request.form.get('nombre', '').strip()
        mail = request.form.get('mail', '').strip()
        contrasena = request.form.get('contrasena', '')



        if not padron or not nombre or not mail or not contrasena:
            flash("Porfavor, complete todos los campos requeridos.", "error")
            return render_template("registro.html")
        
        if len(contrasena) < 8:
            flash("La contraseña debe tener al menos 8 caracteres", "error")
            return render_template("registro.html")

        try:
            padron = int(padron)
        except ValueError:
            flash("Padrón inválido", "error")
            return render_template("registro.html")
        #no se pasa rol porque en el back automaticamente lo pone como docente
        resultado = api.registro(
            padron=padron,
            nombres=nombre,
            mail=mail,
            contrasena=contrasena
        )

        if resultado.get('ok'):
            flash("Usuario creado correctamente. Inicie sesión.", "success")
            return redirect(url_for("auth.login"))
        
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')
    
        return render_template("registro.html")

    return render_template("registro.html")

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

            return redirect(url_for('profesor.asistencia'))
    
        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')

        return render_template('login.html')
    
    return render_template('login.html') #si es get

@auth_bp.route('/contrasena_olvidada', methods = ['GET', 'POST'])
def contrasena_olvidada():

    if request.method == 'POST':
        padron = request.form.get('padron', '').strip()

        if not padron:
            flash("No ingresaste tu padrón", "error")
            return render_template('recuperar-contrasena.html')
        
        try:
            padron = int(padron)
        except ValueError:
            flash("El padrón debe ser un número", "error")
            return render_template('recuperar-contrasena.html')

        resultado = api.contrasena_olvidada(padron)

        if resultado.get('ok'):
            flash("Se ha enviado un correo para restablecer tu contraseña", 'success')

        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')

        return render_template('recuperar-contrasena.html')
    
    return render_template('recuperar-contrasena.html') 

@auth_bp.route('/resetear_contrasena', methods = ['GET', 'POST'])
def resetear_contrasena():
    token = request.args.get('token')
    print(f"token recibido: {token}")

    if not token:
        flash("Token inválido o expirado. Debe pedir un nuevo email de recuperación", 'error')
        return render_template('resetear-contrasena.html', token=token)
    
    if request.method == 'POST':
        contrasena = request.form.get('contrasena', '')
        contrasena_confirmacion = request.form.get('contrasena_confirmacion', '')

        errores = []

        if not contrasena:
            errores.append("No ingresaste la nueva contraseña")

        if not contrasena_confirmacion:
            errores.append("Debes confirmar tu nueva contraseña")

        if len(contrasena) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")

        if contrasena != contrasena_confirmacion:
            errores.append("Las contraseñas no coinciden")

        if errores:
            for e in errores:
                flash(e, 'error')
            
            return render_template('resetear-contrasena.html', token=token)

        resultado = api.resetear_contrasena(token, contrasena)

        if resultado.get('ok'):
            flash("Se restableció correctamente tu contraseña", 'success')

        for mensaje in utils.extraer_mensaje_error(resultado.get('error_response')):
            flash(mensaje, 'error')

        return render_template('resetear-contrasena.html', token=token)
    
    return render_template('resetear-contrasena.html', token=token) 



