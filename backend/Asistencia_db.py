from typing import Any
import mysql.connector
import config


def get_connection(): #Establece conexión con la base de datos.
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )

def get_asistencia():

    con = get_connection()
    cursor = con.cursor(dictionary=True)
    query = "SELECT * FROM Asistencias"
    cursor.execute(query)
    asistencia = cursor.fetchall()
    cursor.close()
    con.close()
    return asistencia

def get_asistencia_id(id):

    con = get_connection()
    cursor = con.cursor(dictionary=True)
    query = "SELECT * FROM Asistencias WHERE Usuarios_padron = %s "
    cursor.execute(query,(id,))
    asistencia = cursor.fetchall()
    cursor.close()
    con.close()
    return asistencia
