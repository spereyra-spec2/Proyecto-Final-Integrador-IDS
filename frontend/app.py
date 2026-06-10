from flask import Flask
from flask_cors import CORS
from src.routes.auth import auth_bp
from src.routes.profesor import profesor_bp
from src.routes.alumno import alumno_bp
from src.routes.ev_notas import notas_bp
from src.routes.evaluaciones import evaluaciones_bp


app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)
app.config['SECRET_KEY'] = 'clave_secreta_ids_2026'


app.register_blueprint(auth_bp, url_prefix="/auth") #sigo ejemplo del repo de cátedra
app.register_blueprint(profesor_bp, url_prefix="/profesor")
app.register_blueprint(alumno_bp, url_prefix="/alumno")
app.register_blueprint(notas_bp, url_prefix='/notas')
app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones" )

if __name__ == "__main__":
    app.run(port=5001, debug=True)
