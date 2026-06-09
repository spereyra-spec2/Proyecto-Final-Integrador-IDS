import mysql.connector
from datetime import datetime
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

def cargar_datos_prueba():
    try:
        conn = mysql.connector.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            database="ids_db"
        )
        cursor = conn.cursor()
        print("Conectado a ids_db exitosamente.")

      
        print("Limpiando datos viejos de forma segura...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE Curso_has_Usuarios;")
        cursor.execute("TRUNCATE TABLE Usuarios_has_Equipos;")
        cursor.execute("TRUNCATE TABLE Equipos;")
        cursor.execute("TRUNCATE TABLE Curso;")
        cursor.execute("TRUNCATE TABLE Usuarios;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

      
        print("Insertando cursos...")
        query_cursos = """
            INSERT INTO Curso (idCurso, nombre, descripcion, created_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);
        """
        cursos_data = [
            (1, "Ingeniería de Software I", "Curso de desarrollo y arquitectura de software", datetime.now()),
            (2, "Base de Datos", "Diseño y optimización de bases de datos relacionales", datetime.now()),
            (3, "Programación Orientada a Objetos", "Fundamentos de POO y patrones de diseño", datetime.now())
        ]
        cursor.executemany(query_cursos, cursos_data)

       
        print("Insertando alumnos...")
        query_usuarios = """
            INSERT INTO Usuarios (padron, rol, nombres, mail, contrasena_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombres=VALUES(nombres);
        """
        
        usuarios_data = [
            (101111, "Alumno", "Juan Pérez", "juan.perez@fi.uba.ar", "hash_simulado_1", datetime.now()),
            (102222, "Alumno", "María Rodríguez", "maria.rod@fi.uba.ar", "hash_simulado_2", datetime.now()),
            (103333, "Alumno", "Lucas Gómez", "lucas.gomez@fi.uba.ar", "hash_simulado_3", datetime.now()),
            (104444, "Alumno", "Ana Martínez", "ana.mtz@fi.uba.ar", "hash_simulado_4", datetime.now()),
            (105555, "Alumno", "Nicolás López", "nico.lopez@fi.uba.ar", "hash_simulado_5", datetime.now())
        ]
        cursor.executemany(query_usuarios, usuarios_data)

       
        print("Vinculando alumnos a los cursos...")
        query_vinculos = """
            INSERT INTO Curso_has_Usuarios (Curso_idCurso, Usuarios_padron)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE Curso_idCurso=VALUES(Curso_idCurso);
        """
        
        vinculos_data = [
            (1, 101111),  # Juan en Ing Soft I
            (1, 102222),  # María en Ing Soft I
            (1, 103333),  # Lucas en Ing Soft I
            (2, 104444),  # Ana en Base de Datos
            (2, 105555),  # Nicolás en Base de Datos
            (2, 101111)   # Juan también cursa Base de Datos
        ]
        cursor.executemany(query_vinculos, vinculos_data)

        
        conn.commit()
        print("\n¡Datos de prueba cargados con éxito de manera segura!")

    except mysql.connector.Error as err:
        print(f"Error al cargar datos: {err}")
        if 'conn' in locals():
            conn.rollback() 
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    cargar_datos_prueba()