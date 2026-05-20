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

        
        print("Insertando cursos...")
        query_cursos = """
            INSERT INTO curso (idCurso, nombre, descripcion, created_at)
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
            INSERT INTO usuarios (padron, rol, nombres, mail, contrasena_hash, cursando_actualmente, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombres=VALUES(nombres);
        """
        
        usuarios_data = [
            (101111, "Alumno", "Juan Pérez", "juan.perez@fi.uba.ar", "hash_simulado_1", 1, datetime.now()),
            (102222, "Alumno", "María Rodríguez", "maria.rod@fi.uba.ar", "hash_simulado_2", 1, datetime.now()),
            (103333, "Alumno", "Lucas Gómez", "lucas.gomez@fi.uba.ar", "hash_simulado_3", 1, datetime.now()),
            (104444, "Alumno", "Ana Martínez", "ana.mtz@fi.uba.ar", "hash_simulado_4", 1, datetime.now()),
            (105555, "Alumno", "Nicolás López", "nico.lopez@fi.uba.ar", "hash_simulado_5", 1, datetime.now())
        ]
        cursor.executemany(query_usuarios, usuarios_data)

    
        print("Vinculando alumnos a los cursos...")
        query_vinculos = """
            INSERT INTO curso_has_usuarios (curso_idcurso, usuarios_padron)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE curso_idcurso=VALUES(curso_idcurso);
        """
        
        vinculos_data = [
            (1, 101111),  
            (1, 102222),  
            (1, 103333),  
            (2, 104444),  
            (2, 105555),  
            (2, 101111)   
        ]
        
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE curso_has_usuarios;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        cursor.executemany(query_vinculos, vinculos_data)

        
        conn.commit()
        print("\n¡Datos de prueba cargados con éxito de manera segura!")

    except mysql.connector.Error as err:
        print(f"Error al cargar datos: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    cargar_datos_prueba()