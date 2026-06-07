from flask import Flask

from src.routes.ev_notas import notas_bp

app = Flask(__name__, 
    template_folder= 'templates',
    static_folder='static'
)


app.register_blueprint(notas_bp, url_prefix='/notas')


if __name__ == '__main__':
    app.run(port=5000, debug=True)