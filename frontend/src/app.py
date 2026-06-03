import os
import requests
from flask import Flask, render_template, request, redirect, url_for

base_path = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, 
    template_folder=os.path.join(base_path, 'templates'),
    static_folder=os.path.join(base_path, 'static')
)

API_BASE_URL = "http://127.0.0.1:3006/api"


@app.route('/notas/ver', methods=['GET'])
def vista_ver_nota():
    
    curso_id = request.args.get('curso_id')

    id_ev = request.args.get('id_ev')
    
    identificador = request.args.get('identificador')  

    if not curso_id or not id_ev or not identificador:
        return render_template('ver_nota.html', nota=None, error=None)

    API = f"{API_BASE_URL}/{curso_id}/evaluaciones/{id_ev}/notas"
    

    query_parameters = {
        'padron': identificador,
        'id_equipo': identificador
    }

    try:
        respuesta = requests.get(API, params=query_parameters)
        
        if respuesta.status_code == 200:
            nota = respuesta.json()
            return render_template('ver_nota.html', 
                                   nota=nota, 
                                   error=None,
                                   curso_id=curso_id, 
                                   id_evaluaciones=id_ev, 
                                   identificador=identificador)
        else:

            msg_error = respuesta.json().get('description', 'No se encontró la calificación con los datos ingresados.')
            return render_template('ver_nota.html', 
                                   nota=None, 
                                   error=msg_error,
                                   curso_id=curso_id,
                                   id_evaluaciones=id_ev,
                                   identificador=identificador)

    except requests.exceptions.ConnectionError:
        return render_template('ver_nota.html', nota=None, error="Error de conexión: El servidor está apagado.")



@app.route('/notas/cargar', methods=['GET'])
def vista_cargar_nota():
    
    estado = request.args.get('estado')
    return render_template('cargar_nota.html', estado=estado)


@app.route('/notas/guardar', methods=['POST'])
def procesar_guardado():
    curso_id = request.form.get('curso_id')
    id_evaluacion = request.form.get('id_evaluacion')
    identificador = request.form.get('padron')
    puntaje = request.form.get('puntaje')

    API = f"{API_BASE_URL}/notas/guardar"
    json = {"curso_id": int(curso_id), "id_evaluacion": int(id_evaluacion), "padron": int(identificador), "puntaje": float(puntaje)}

    try:
        respuesta = requests.post(API, json=json)
        
        if respuesta.status_code == 201:
            return redirect(url_for('cargar_nota', estado='exito'))
        else:
            error_api = respuesta.json().get('description', 'Error al intentar guardar la nota.')
            return f"<h3>Error en el Servidor de Datos: {error_api}</h3><a href='/notas/cargar'>Volver a intentar</a>", respuesta.status_code

    except requests.exceptions.ConnectionError:
        return "<h3>Error de conexión: No se pudo conectar al servidor.</h3>", 500



@app.route('/notas/editar', methods=['GET'])
def vista_editar_nota():

    contexto = {'curso_id': request.args.get('curso_id'), 'id_ev': request.args.get('id_ev'), 'padron': request.args.get('padron')}

    return render_template('editar_nota.html', **contexto)


@app.route('/notas/actualizar', methods=['POST'])
def procesar_actualizacion():

    curso_id = request.form.get('curso_id')
    id_ev = request.form.get('id_evaluacion')
    identificador = request.form.get('identificador')
    nuevo_puntaje = request.form.get('puntaje')

    API = f"{API_BASE_URL}/curso/{curso_id}/evaluaciones/{id_ev}/notas"
    query_parameters = {'padron': identificador, 'id_equipo': identificador}
    json = {'puntaje': float(nuevo_puntaje)}

    try:
        respuesta = requests.patch(API, params=query_parameters, json=json)
        
        if respuesta.status_code == 200:
            return redirect(f"/notas/ver?curso_id={curso_id}&id_ev={id_ev}&padron={identificador}")
        else:
            error_api = respuesta.json().get('description', 'No se pudo actualizar la nota.')
            return f"<h3>Error al actualizar: {error_api}</h3><a href='javascript:history.back()'>Regresar</a>", respuesta.status_code

    except requests.exceptions.ConnectionError:
        return "<h3>Error crítico: El servidor no responde.</h3>", 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)