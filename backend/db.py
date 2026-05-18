from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, MetaData
import mysql.connector
import config

def get_connection(): #Establece conneción con la base de datos.
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )

db = SQLAlchemy()
metadata = MetaData()
usuarios = Table("usuarios", metadata,
    Column("padron", Integer, primary_key=True),
    Column("rol", String(20)),
    Column("nombres", String(255)),
    Column("mail", String(255)),
)
asistencias = Table("asistencias", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("asistio", Boolean),
    Column("fecha", Date),
    Column("padron", Integer),
    Column("justificado", Boolean),
    Column("hash_qr", String(512)),
)



