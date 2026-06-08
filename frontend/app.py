import os
import re
from flask import Flask, render_template, request,redirect, url_for, flash
import requests
import re
from flask_cors import CORS

BACK_URL = "http://localhost:5000"
FRONT_URL = "http://localhost:5001"

base_path = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
    template_folder=os.path.join(base_path, 'templates'),
    static_folder=os.path.join(base_path, 'static')
)

CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login")
def sin_autorizacion():
    return render_template("base.html")

@app.route('/asistencia/profe')
def asistencia_profe():
    qr_generado = False
    if request.args.get('generar'):
        respuesta = requests.get(f"{BACK_URL}/api/asistencia/generar-qr")
        if respuesta.status_code == 202:
            qr_generado = True

    resp_asistencias = requests.get(f"{BACK_URL}/api/asistencia")
    asistencias = resp_asistencias.json() if resp_asistencias.status_code == 200 else []

    return render_template('profesor-asistencia.html', qr_generado=qr_generado, asistencias=asistencias)

@app.route('/asistencia/formulario')
def formulario_asistencia():
    token = request.args.get('token','')
    return render_template('alumno-asistencia.html', token=token)

@app.route('/asistencia/registrar', methods=['POST'])
def registrar_asistencia():
    padron = request.form.get('padron')
    token = request.form.get('token')

    respuesta = requests.post(
        f"{BACK_URL}/api/asistencia/confirmar-asistencia",
        json={"padron":padron, "token": token}
    )

    datos = respuesta.json()

    if respuesta.status_code == 200:
        return render_template('alumno-asistencia.html', token=token, mensaje="asistencia registrada", exito=True)

    else:
        return render_template("alumno-asistencia.html", token=token, mensaje=datos.get("mensajes", "error al registrar asistencia"), exito=False)

@app.route('/asistencia/qr-imagen')
def qr_imagen():
    respuesta = requests.get(f"{BACK_URL}/api/asistencia/qr-imagen", stream=True)
    return respuesta.content, 200, {'Content-Type': 'image/png'}


@app.route("/asistencia", methods=["GET", "POST"])
def obtener_asistencia():
    token = request.args.get('token')
    headers = {
        "Authorization": f"Bearer {token}"
    }
    if request.method == 'POST':
        padron = request.form.get('padron', '').strip()

        if not padron:
            return redirect(url_for('obtener_asistencia'))
        
        regular_expresion = re.compile(r"^[1-9][0-9]{5}$")
        padron_bool= bool(regular_expresion.match(str(padron)))
        if not(padron_bool):
            return redirect(url_for('obtener_asistencia'))
        return redirect(url_for("obtener_asistencia_padron", padron=padron))


    try:
        respuesta_back = requests.get(f"{BACK_URL}/api/asistencia",headers=headers)
        
        if respuesta_back.status_code in [401, 403]:
            return redirect(url_for("sin_autorizacion"))
        if respuesta_back.status_code != 200:
            return "Error interno al conectar con el servidor de datos", 500
        datos_asistencia = respuesta_back.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el Back: {e}")
        datos_asistencia = [] 
    return render_template("profesor-asistencia.html", asistencias=datos_asistencia)


@app.route('/asistencia/<padron>', methods=["GET"])
def obtener_asistencia_padron(padron):
    token = request.args.get('token')
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        respuesta_back = requests.get(f"{BACK_URL}/api/asistencia/{padron}",headers=headers)
        
        if respuesta_back.status_code in [401, 403]:
            return redirect(url_for("sin_autorizacion"))
        if respuesta_back.status_code != 200:
            return "Error interno al conectar con el servidor de datos", 500
        datos_asistencia = respuesta_back.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el Back: {e}")
        datos_asistencia = [] 
    return render_template("asistencia_padron.html", asistencias=datos_asistencia)

@app.route('/evaluaciones', methods=['GET', 'POST'])
def evaluaciones():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        descripcion = request.form.get('descripcion')
        fecha = request.form.get('fecha')
        curso_id = request.form.get('curso_id')
        try:
            respuesta = requests.post(f"{BACK_URL}/api/evaluaciones", json={
                "tipo": tipo,
                "descripcion": descripcion,
                "fecha": fecha,
                "Curso_idCurso": curso_id
            })
            if respuesta.status_code == 201:
                flash('Evaluación creada exitosamente', 'success')
            else:
                flash('Error al crear la evaluación: {}'.format(respuesta.json().get('error', 'Error desconocido')), 'danger')
        except requests.exceptions.RequestException as e:
            flash('Error de conexión con el servidor: {}'.format(str(e)), 'danger')
    return render_template('profesor-evaluaciones.html')


if __name__ == '__main__':
    app.run(port=5001, debug=True)





