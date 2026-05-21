host: str = "localhost"
user: str = "root"
password: str = "root"
database: str = "ids_db"
MODEL_PATH: str = "src/models/init_db.sql"

URL_BASE: str = "api"

# En producción no debería estar hardcodeada; usar variable de entorno o similar (?)
SECRET_KEY = "ids2026_puntoycoma"