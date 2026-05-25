import mysql.connector
from db import get_connection
import src.utils.errors as errors
from src.utils.seguridad import hashear_contrasena, comparar_contrasena
from flask import jsonify
from datetime import datetime

def login_user(padron, contrasena):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Usuarios where padron=%s", (padron,))
        usuario_logueado = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return None, errors.server_error(e)

    if not usuario_logueado:
        return None, errors.no_registrado(padron)
    
    contrasena_correcta = comparar_contrasena(contrasena, usuario_logueado["contrasena_hash"])

    if not contrasena_correcta:
        return None, errors.contrasena_incorrecta()

    return usuario_logueado, None


def alta_usuario(padron, rol, nombres, mail, contrasena):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        contrasena_hasheada = hashear_contrasena(contrasena)
        cursor.execute("INSERT INTO Usuarios (padron, rol, nombres, mail, contrasena_hash, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (padron, rol, nombres, mail, contrasena_hasheada, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        return errors.server_error(e)
    
    return None

def existe_usuario(padron):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Usuarios where padron=%s", (padron,))
        usuario= cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return None, errors.server_error(e)
    
    if usuario:
        return True, None
    
    return False, None
    

def actualizar_contrasena(padron, contrasena_hash):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Usuarios
            SET contrasena_hash = %s
            WHERE padron = %s
            """,
            (contrasena_hash, padron)
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception:
        return errors.server_error()

    return None

def obtener_mail_usuario(padron):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT mail from Usuarios WHERE padron=%s", (padron,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return None, errors.server_error(e)
    
    if not resultado:
        return None, errors.no_registrado(padron)
    
    return resultado["mail"], None