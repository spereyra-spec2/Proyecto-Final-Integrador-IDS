import mysql.connector
from db import get_connection

def validar_id(int: id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"SELECT * FROM usuarios WHERE padron = {id}"
    try:
        cursor.execute(query)
        return cursor.fetchone()

    finally:
        conn.close()
        cursor.close()



    

