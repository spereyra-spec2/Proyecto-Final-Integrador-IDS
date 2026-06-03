from flask import Flask, render_template
from flask_cors import CORS
from src.routes.auth import auth_bp
from src.routes.profesor import profesor_bp
from src.routes.alumno import alumno_bp


app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)
app.config['SECRET_KEY'] = 'clave_secreta_ids_2026'

# @app.route('/')
# def index():
#     return render_template('alumno-inicio.html')

app.register_blueprint(auth_bp, url_prefix="/api/auth") #sigo ejemplo del repo de cátedra
app.register_blueprint(profesor_bp, url_prefix="/api/profesor")
app.register_blueprint(alumno_bp, url_prefix="/api/alumno")

if __name__ == "__main__":
    app.run(port=5001, debug=True)