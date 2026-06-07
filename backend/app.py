from flask import Flask
from flask_cors import CORS

#from auth import auth_db
from backend.init_db import init_db
from src.routes.auth.auth import auth_bp
from frontend.auth_frontend import frontend_bp

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(frontend_bp)


try:
    init_db()
except Exception as e:
    print(f"error al inicializar la base de datos: {e}")
    exit(1)

for rule in app.url_map.iter_rules():
    print(rule.endpoint, rule)

if __name__ == "__main__":
    app.run(port=3006, debug=True)
