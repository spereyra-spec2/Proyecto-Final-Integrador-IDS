import os
import mysql.connector
from config import user, password, host

def init_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    
    sql_file_path = os.path.join(current_dir, "src", "models", "init_db.sql")

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = mysql.connector.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
    )

    cursor = conn.cursor()
    for statement in sql.split(";"):
        if statement.strip():
            print(statement)
            cursor.execute(statement)
            conn.commit()
            print("Instrucción ejecutada")

    cursor.close()
    conn.close()