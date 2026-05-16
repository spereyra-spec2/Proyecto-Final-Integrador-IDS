from flask import Flask
from flask_cors import CORS
from routes.usuarios import usuarios_bp
from init_db import init_db

app = Flask(__name__)
CORS(app)

app.register_blueprint(usuarios_bp, url_prefix="/usuarios")

try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)


if __name__ == "__main__":
    app.run(port=3306, debug=True)
