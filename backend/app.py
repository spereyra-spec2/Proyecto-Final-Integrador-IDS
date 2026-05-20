from flask import Flask
from flask_cors import CORS
from init_db import init_db
from src.routes.equipos import equipos_bp

app = Flask(__name__)
CORS(app)
app.config["JSON_SORT_KEYS"] = False
app.register_blueprint(equipos_bp)

try:
    init_db()
except Exception as e:
    print(f"Error al inicializar la base de datos: {e}")
    exit(1)


if __name__ == "__main__":
    app.run(port=5000, debug=True)