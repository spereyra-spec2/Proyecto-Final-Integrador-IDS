import mysql.connector
import config

def get_connection():
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

def get_asistencia():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    query = "SELECT * FROM Asistencias"
    cursor.execute(query)
    asistencia = cursor.fetchall()
    cursor.close()
    con.close()
    return asistencia

def get_asistencia_padron(padron):
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    query = "SELECT * FROM Asistencias WHERE Usuarios_padron = %s "
    cursor.execute(query,(padron,))
    asistencia = cursor.fetchall()
    cursor.close()
    con.close()
    return asistencia
