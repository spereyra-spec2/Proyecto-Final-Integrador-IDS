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

@app.route('/asistencia/formulario')
def formulario_asistencia():
    return render_template('formulario_asistencia.html')

@app.route('/asistencia/alumnos')
def asistencia_alumnos():
    return render_template('alumno-asistencia.html')

@app.route('/asistencia/profe')
def asistencia_profe():
    return render_template('profesor-asistencia.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

