from flask import Flask
from flask_cors import CORS
from init_db import init_db
from src.routes.auth.auth import auth_bp
from src.routes.evaluaciones import evaluaciones_bp
import config
from mail import mail

app = Flask(__name__)

CORS(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'gestion.academica.ids@gmail.com'
app.config['MAIL_PASSWORD'] = 'xdkv alji fnmx euxz'
app.config["SECRET_KEY"] = config.SECRET_KEY


app.register_blueprint(auth_bp, url_prefix="/api/auth")

mail.init_app(app)

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
