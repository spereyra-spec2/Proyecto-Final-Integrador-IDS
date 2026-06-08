
from flask import Flask, render_template, request,redirect, url_for, flash
from flask_cors import CORS
from src.routes.asistencia import asistencia_bp


app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

app.register_blueprint(asistencia_bp, url_prefix='/asistencia')

if __name__ == '__main__':
    app.run(port=5001, debug=True)





