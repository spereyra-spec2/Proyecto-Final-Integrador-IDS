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


def obtener_alumno_por_padron(padron): # Devuelve todas las columnas del usuario con rol 'estudiantes' que tenga el padrón indicado 
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM usuarios WHERE padron = %s AND rol = 'estudiantes'",
            (padron,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def ya_usado_token(token): # Verifica si un token QR ya fue escaneado (anti‑replay)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM asistencias WHERE hash_qr = %s LIMIT 1", (token,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

def registrar_asistencia(padron, token): # Registra presente en la tabla asistencias. Retorna True si se insertó. 
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO asistencias (asistio, fecha, padron, justificado, hash_qr) VALUES (1, CURDATE(), %s, 0, %s)",
            (padron, token)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
