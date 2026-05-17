from flask import Flask
from flask_cors import CORS
from init_db import init_db

app = Flask(__name__)
CORS(app)


try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)


if __name__ == "__main__":
    app.run(port=3006, debug=True)