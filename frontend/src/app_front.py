import os
from flask import Flask, render_template, request,redirect

#Sirve para evaluar respestas de la API
import requests


base_path = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, 
    template_folder=os.path.join(base_path, 'templates'),
    static_folder=os.path.join(base_path, 'static')
)

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/notas/cargar')
def cargar():
    return render_template('cargar_nota.html')

@app.route('/notas/ver/<padron>')
def ver_notas(padron):

    curso_id = request.args.get('curso_id')
    
    id_ev = request.args.get('id_ev')
    
    padron = request.args.get('padron')
    
    id_equipo = request.args.get('id_equipo')
    
    url_api = f"http://127.0.0.1:3006/api/curso/{curso_id}/evaluaciones/{id_ev}/notas"
    
    query_parameters = {}


    if padron:
        query_parameters['padron'] = padron
    elif id_equipo:
        query_parameters['id_equipo'] = id_equipo

    try:
        respuesta = requests.get(url_api, params=query_parameters)
        
        if respuesta.status_code == 200:
            datos_nota = respuesta.json()
            error_msg = None
        else:
            datos_nota = None
            error_msg = respuesta.json().get('description', 'No se encontró la nota')
            
    except requests.exceptions.ConnectionError:
        return "Error: No se pudo conectar con la API", 500

    return render_template('ver_nota.html', nota=datos_nota, error=error_msg,curso_id=curso_id, id_evaluaciones=id_ev, id=padron if padron else id_equipo, padron=padron)

@app.route('/notas/editar')
def editar_nota():

    curso_id = request.form.get('curso_id')
    id_ev = request.form.get('id_evaluacion')
    padron = request.form.get('padron')
    id_equipo = request.form.get('id_equipo')
    nuevo_puntaje = request.form.get('puntaje')

    url_api = f"http://127.0.0.1:3006/api/curso/{curso_id}/evaluaciones/{id_ev}/notas"
    
    query_parameters = {'padron': padron} if padron else {'id_equipo': id_equipo}
    
    nota_a_cargar = {'puntaje': float(nuevo_puntaje)}

    try:
        respuesta = requests.patch(url_api, params=query_parameters, json=nota_a_cargar)
        
        if respuesta.status_code == 200:
            return redirect(f"/notas/ver?curso_id={curso_id}&id_ev={id_ev}&padron={padron or ''}&id_equipo={id_equipo or ''}&status=updated")
        else:
            return f"Error en la API: {respuesta.json().get('description', 'No se pudo actualizar')}", respuesta.status_code

    except requests.exceptions.ConnectionError:
        return "Error: No se pudo conectar con la API.", 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

