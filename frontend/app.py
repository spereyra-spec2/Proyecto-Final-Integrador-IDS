import os
from flask import Flask

from src.routes.ev_notas import notas_bp

base_path = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, 
    template_folder=os.path.join(base_path, 'templates'),
    static_folder=os.path.join(base_path, 'static')
)


app.register_blueprint(notas_bp, url_prefix='/notas')


if __name__ == '__main__':
    app.run(port=5000, debug=True)