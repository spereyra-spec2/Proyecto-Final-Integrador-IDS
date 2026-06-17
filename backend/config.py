import os

host: str = "localhost"
user: str = "root"
password: str = "P!assW0rd33"
database: str = "ids_db"

# generacion de QR
SECRET_KEY = "djioadjoi"
QR_EXPIRATION_SECONDS = 900 # 15 min
QR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_asistencia.png")
BACK_URL = "http://localhost:5000"
FRONT_URL = "http://localhost:5001"
