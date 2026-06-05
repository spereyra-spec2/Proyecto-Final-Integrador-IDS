import os
from flask import Flask, render_template, request,redirect
import requests

BACK_URL = "http://localhost:5000"
FRONT_URL = "http://localhost:5001"

base_path = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, 
    template_folder=os.path.join(base_path, 'templates'),
    static_folder=os.path.join(base_path, 'static')
)

@app.route('/')
def home():
    return render_template('base.html')

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

if __name__ == '__main__':
    app.run(port=5001, debug=True)

