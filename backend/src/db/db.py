import mysql.connector
import config


def get_connection(): #Establece conneción con la base de datos.
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )