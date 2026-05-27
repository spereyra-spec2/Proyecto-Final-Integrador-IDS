from config import user, password, host
import mysql.connector
import os

def init_db():
    sql_path = os.path.join(os.path.dirname(__file__), "src", "models", "init_db.sql")
    with open(sql_path) as f:
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
