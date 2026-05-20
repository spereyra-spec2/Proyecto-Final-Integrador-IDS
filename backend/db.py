import mysql.connector
import config

def get_connection(): #Establece conneción con la base de datos.
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        port=3306,
        password=config.password,
        database=config.database
    )


def obtener_alumno_por_padron(padron):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM Usuarios WHERE padron = %s AND rol = 'Alumno'",
            (padron,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

