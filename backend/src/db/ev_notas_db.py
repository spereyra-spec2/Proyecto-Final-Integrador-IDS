from db import get_connection

def validar_id(id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM usuarios WHERE padron = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()

def validar_equipo(id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM equipos WHERE idEquipos = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()

def validar_curso (id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM cursos WHERE id = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()

def validar_evaluacion (id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM evaluaciones WHERE id = %s"
    try:
        cursor.execute(query, (id,))
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()

    

