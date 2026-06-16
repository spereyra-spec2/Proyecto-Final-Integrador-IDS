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
            INSERT INTO Curso (idCurso, nombre, codigo, descripcion, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), codigo = VALUES(codigo);
        """
        cursos_data = [
            (1, "Ingeniería de Software I", "AB123", "Curso de desarrollo y arquitectura de software", datetime.now()),
            (2, "Base de Datos", "CD123", "Diseño y optimización de bases de datos relacionales", datetime.now()),
            (3, "Programación Orientada a Objetos", "AB456", "Fundamentos de POO y patrones de diseño", datetime.now())
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

        # --- Additional test users ---
        print("Insertando más usuarios de prueba...")
        extra_usuarios = [
            (106666, "Alumno", "Camila Torres", "camila.torres@fi.uba.ar", "hash_simulado_6", datetime.now()),
            (107777, "Alumno", "Diego Fernández", "diego.fernandez@fi.uba.ar", "hash_simulado_7", datetime.now()),
            (108888, "Alumno", "Sofía Herrera", "sofia.herrera@fi.uba.ar", "hash_simulado_8", datetime.now()),
            (900001, "Docente", "Prof. Arturo Gómez", "arturo.gomez@fi.uba.ar", "hash_prof_1", datetime.now())
        ]
        cursor.executemany(query_usuarios, extra_usuarios)

        # Link extra users to courses
        extra_vinculos = [
            (1, 106666),
            (1, 107777),
            (3, 108888),
            (1, 900001)
        ]
        cursor.executemany(query_vinculos, extra_vinculos)

        # --- Insert equipos (teams) and memberships ---
        print("Insertando equipos de prueba y asignando integrantes...")
        equipos_to_create = [
            ("Grupo Alpha", "ALPHA1", 1),
            ("Grupo Beta", "BETA22", 1),
            ("DB Squad", "DB123", 2),
            ("POO Team", None, 3),
            ("Equipo Mixto", "MIXED99", 1)
        ]

        query_insert_equipo = """
            INSERT INTO Equipos (nombre, access_code, Curso_idCurso, created_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), Curso_idCurso=VALUES(Curso_idCurso);
        """

        created_ids = {}
        for nombre, code, curso in equipos_to_create:
            cursor.execute(query_insert_equipo, (nombre, code, curso, datetime.now()))
            # try to find id by access_code if present, otherwise by name+curso
            if code:
                cursor.execute("SELECT idEquipos FROM Equipos WHERE access_code = %s", (code,))
            else:
                cursor.execute("SELECT idEquipos FROM Equipos WHERE nombre = %s AND Curso_idCurso = %s", (nombre, curso))
            row = cursor.fetchone()
            if row:
                created_ids[nombre] = row[0]

        # memberships: map equipo name to padrones
        memberships = {
            "Grupo Alpha": [101111, 102222, 106666],
            "Grupo Beta": [103333, 107777],
            "DB Squad": [104444, 105555],
            "POO Team": [103333],
            "Equipo Mixto": [101111, 108888]
        }

        query_upsert_members = """
            INSERT INTO Usuarios_has_Equipos (Usuarios_padron, Equipos_idEquipos, activo, activo_desde)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE activo=VALUES(activo), activo_desde=VALUES(activo_desde);
        """

        for equipo_name, padrones in memberships.items():
            equipo_id = created_ids.get(equipo_name)
            if not equipo_id:
                continue
            for p in padrones:
                cursor.execute(query_upsert_members, (p, equipo_id, 1, datetime.now()))


        
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
