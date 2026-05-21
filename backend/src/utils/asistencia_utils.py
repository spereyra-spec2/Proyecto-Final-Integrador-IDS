from src.db.db import get_connection
import os
import qrcode

def alumno_asistio(padron):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Asistencias WHERE Usuarios_padron = %s AND DATE(fecha) = CURDATE() LIMIT 1""", (padron,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

def registrar_asistencia(padron):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Asistencias (asistio, fecha, justificado, Usuarios_padron) VALUES (1, NOW(), 0, %s)", (padron))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def hacer_y_guardar_qr(url):
    img = qrcode.make(url)

    os.makedirs("static", exist_ok=True)
    filepath = os.path.join(".","qr_asistencia.png")
    img.save(filepath)
    print(f"QR generado y guardado en {filepath}")
