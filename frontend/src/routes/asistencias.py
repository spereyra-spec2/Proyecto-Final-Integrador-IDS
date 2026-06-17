import re
from flask import Flask, render_template, request,redirect, url_for, flash, Blueprint
import requests
import re

from datetime import date
import time

BACK_URL = "http://localhost:5000"
FRONT_URL = "http://localhost:5001"
asistencias_bp = Blueprint('asistencia', __name__)

@asistencias_bp.route('profesor/cursos/<int:idCurso>/asistencias/formulario')
def formulario_asistencia(idCurso):
    token = request.args.get('token','')
    return render_template('alumno-asistencia.html', token=token, idCurso=idCurso)

@asistencias_bp.route('profesor/cursos/<int:idCurso>/asistencia/registrar', methods=['POST'])
def registrar_asistencia(idCurso):
    padron = request.form.get('padron')
    token = request.form.get('token')

    respuesta = requests.post(
        f"{BACK_URL}/api/cursos/{idCurso}/asistencias/confirmar-asistencia",
        json={"padron":padron, "token": token}
    )
    datos = respuesta.json()

    if respuesta.status_code == 200:
        return render_template('alumno-asistencia.html', token=token, mensaje="asistencia registrada", exito=True, idCurso=idCurso)

    else:
        return render_template("alumno-asistencia.html", token=token, mensaje=datos.get("mensajes", "error al registrar asistencia"), exito=False, idCurso=idCurso)

@asistencias_bp.route('profesor/cursos/<int:idCurso>/asistencia/qr-imagen')
def qr_imagen(idCurso):
    respuesta = requests.get(f"{BACK_URL}/api/cursos/{idCurso}/asistencias/qr-imagen", stream=True)
    return respuesta.content, 200, {'Content-Type': 'image/png'}


@asistencias_bp.route("profesor/cursos/<int:idCurso>/asistencia", methods=["GET", "POST"])
def asistencia_profe(idCurso):
    token = request.args.get('token')
    headers = {
        "Authorization": f"Bearer {token}"
    }
    if request.method == 'POST':
        padron = request.form.get('padron', '').strip()

        if not padron:
            return redirect(url_for('asistencia.asistencia_profe', idCurso=idCurso))
        
        regular_expresion = re.compile(r"^[1-9][0-9]{5}$")
        padron_bool= bool(regular_expresion.match(str(padron)))
        if not(padron_bool):
            return redirect(url_for('asistencia.asistencia_profe', idCurso=idCurso))
        
        return redirect(url_for("asistencia.obtener_asistencia_padron", padron=padron, idCurso=idCurso))

    qr_generado = False
    if request.args.get('generar'):
        respuesta = requests.get(f"{BACK_URL}/api/cursos/{idCurso}/asistencias/generar-qr")
        if respuesta.status_code == 202:
            qr_generado = True

    resp_asistencias = requests.get(f"{BACK_URL}/api/cursos/{idCurso}/asistencias") 
    asistencias = resp_asistencias.json() if resp_asistencias.status_code == 200 else []

    return render_template('profesor-asistencia.html', qr_generado=qr_generado, asistencias=asistencias, fecha_hoy =date.today().strftime("%d %b %Y"), idCurso=idCurso,  ts=int(time.time()))


@asistencias_bp.route('profesor/cursos/<int:idCurso>/asistencia/<padron>', methods=["GET"])
def obtener_asistencia_padron(padron, idCurso):
    token = request.args.get('token')
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        respuesta_back = requests.get(f"{BACK_URL}/api/cursos/{idCurso}/asistencias/{padron}",headers=headers)
        
        if respuesta_back.status_code in [401, 403]:
            return redirect(url_for("sin_autorizacion"))
        if respuesta_back.status_code not in [200, 204]:
            return "Error interno al conectar con el servidor de datos", 500
        datos_asistencia = respuesta_back.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el Back: {e}")
        datos_asistencia = [] 
    return render_template("asistencia_padron.html", asistencias=datos_asistencia, idCurso=idCurso)

