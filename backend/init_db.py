import os
from config import user, password, host
import mysql.connector

def init_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(base_dir, "src", "models", "init_db.sql")
    
    with open(sql_path) as f:
        sql = f.read()

    conn = mysql.connector.connect(
        host=host,
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

if __name__ == "__main__":
    init_db()
