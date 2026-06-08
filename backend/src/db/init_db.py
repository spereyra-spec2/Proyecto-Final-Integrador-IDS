from config import user, password, host
import mysql.connector

def init_db():
    with open("src/db/init_db.sql") as f:
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
