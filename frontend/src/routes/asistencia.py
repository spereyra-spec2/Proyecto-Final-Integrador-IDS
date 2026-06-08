from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
import requests
from src.utils.contants import API_BASE_URL
import re


asistencia_bp = Blueprint('asistencia', __name__)


@asistencia_bp.route('/asistencia/profe')
def asistencia_profe():
    qr_generado = False
    if request.args.get('generar'):
        respuesta = requests.get(f"{API_BASE_URL}/api/asistencia/generar-qr")
        if respuesta.status_code == 202:
            qr_generado = True

    resp_asistencias = requests.get(f"{API_BASE_URL}/api/asistencia")
    asistencias = resp_asistencias.json() if resp_asistencias.status_code == 200 else []

    return render_template('profesor-asistencia.html', qr_generado=qr_generado, asistencias=asistencias)

@asistencia_bp.route('/asistencia/formulario')
def formulario_asistencia():
    token = request.args.get('token','')
    return render_template('alumno-asistencia.html', token=token)

@asistencia_bp.route('/asistencia/registrar', methods=['POST'])
def registrar_asistencia():
    padron = request.form.get('padron')
    token = request.form.get('token')

    respuesta = requests.post(
        f"{API_BASE_URL}/api/asistencia/confirmar-asistencia",
        json={"padron":padron, "token": token}
    )

    datos = respuesta.json()

    if respuesta.status_code == 200:
        return render_template('alumno-asistencia.html', token=token, mensaje="asistencia registrada", exito=True)

    else:
        return render_template("alumno-asistencia.html", token=token, mensaje=datos.get("mensajes", "error al registrar asistencia"), exito=False)

@asistencia_bp.route('/asistencia/qr-imagen')
def qr_imagen():
    respuesta = requests.get(f"{API_BASE_URL}/api/asistencia/qr-imagen", stream=True)
    return respuesta.content, 200, {'Content-Type': 'image/png'}


@asistencia_bp.route("/asistencia", methods=["GET", "POST"])
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
        respuesta_back = requests.get(f"{API_BASE_URL}/api/asistencia",headers=headers)
        
        if respuesta_back.status_code in [401, 403]:
            return redirect(url_for("sin_autorizacion"))
        if respuesta_back.status_code != 200:
            return "Error interno al conectar con el servidor de datos", 500
        datos_asistencia = respuesta_back.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el Back: {e}")
        datos_asistencia = [] 
    return render_template("profesor-asistencia.html", asistencias=datos_asistencia)


@asistencia_bp.route('/asistencia/<padron>', methods=["GET"])
def obtener_asistencia_padron(padron):
    token = request.args.get('token')
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        respuesta_back = requests.get(f"{API_BASE_URL}/api/asistencia/{padron}",headers=headers)
        
        if respuesta_back.status_code in [401, 403]:
            return redirect(url_for("sin_autorizacion"))
        if respuesta_back.status_code != 200:
            return "Error interno al conectar con el servidor de datos", 500
        datos_asistencia = respuesta_back.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el Back: {e}")
        datos_asistencia = [] 
    return render_template("asistencia_padron.html", asistencias=datos_asistencia)
