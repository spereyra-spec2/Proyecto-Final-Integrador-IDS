from src.db.db import get_connection
import os
import qrcode
import re
import jwt
from config import  SECRET_KEY, QR_PATH

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
        cursor.execute("INSERT INTO Asistencias (asistio, fecha, justificado, Usuarios_padron) VALUES (1, NOW(), 0, %s)", (padron,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def hacer_y_guardar_qr(url):
    img = qrcode.make(url)
    img.save(QR_PATH)
    print(f"QR generado y guardado en {QR_PATH}")

def validar_padron(padron):
    regular_expresion = re.compile(r"^[1-9][0-9]{5}$")
    return bool(regular_expresion.match(str(padron)))

def existe_padron(padron):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Asistencias WHERE Usuarios_padron = %s""", (padron,))
        return cursor.rowcount() > 0
    finally:
        cursor.close()
        conn.close()
    

def verificar_token(headers, roles_permitidos):
    if "Authorization" not in headers:
        return False
        
    encoded_token = headers["Authorization"]

    try:
        payload = jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
        rol_usuario = payload.get("rol")

        if rol_usuario in roles_permitidos:
            return True
            
        return False
    except jwt.PyJWTError: 
        return False
