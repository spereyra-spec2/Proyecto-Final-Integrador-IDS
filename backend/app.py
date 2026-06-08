from flask import Flask
from flask_cors import CORS
from init_db import init_db
from src.routes.auth.auth import auth_bp
from src.routes.api_ev_notas import ev_notas_bp
from mail import mail
app = Flask(__name__)

CORS(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'gestion.academica.ids@gmail.com'
app.config['MAIL_PASSWORD'] = 'xdkv alji fnmx euxz'


app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(ev_notas_bp, url_prefix="/api/notas")
mail.init_app(app)

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)


if __name__ == "__main__":
    app.run(port=3006, debug=True)
