import os
import re
from flask import Flask, render_template, request,redirect, url_for, flash
import requests
import re
from flask_cors import CORS
from routes.evaluaciones import evaluaciones_bp
from routes.asistencias import asistencias_bp
from datetime import date

BACK_URL = "http://localhost:5000"
FRONT_URL = "http://localhost:5001"


base_path = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
    template_folder=os.path.join(base_path, 'templates'),
    static_folder=os.path.join(base_path, 'static')
)
CORS(app)

app.register_blueprint(asistencias_bp, url_prefix='/asistencia')


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login")
def sin_autorizacion():
    return render_template("base.html")

if __name__ == '__main__':
    app.run(port=5001, debug=True)





