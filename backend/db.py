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

def ip_registrado(ip_address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Asistencias WHERE ip_address = %s AND DATE(fecha) = CURDATE() LIMIT 1", (ip_address,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

def registrar_asistencia(padron, ip_address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Asistencias (asistio, fecha, justificado, Usuarios_padron, ip_address) VALUES (1, NOW(), 0, %s, %s)", (padron, ip_address))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def alumno_asistio(padron):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Asistencias WHERE Usuarios_padron = %s AND DATE(fecha) = CURDATE() LIMIT 1""", (padron,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
