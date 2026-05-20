import mysql.connector
from db import get_connection

def validar_id(int: id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM usuarios WHERE padron = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()



def validar_curso (int: id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM cursos WHERE id = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()

def validar_evaluacion (int: id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM evaluaciones WHERE id = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()

    

