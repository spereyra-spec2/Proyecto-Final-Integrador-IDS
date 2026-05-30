CREATE DATABASE IF NOT EXISTS ids_db;
USE ids_db;
CREATE TABLE IF NOT EXISTS usuarios (
    padron INT NOT NULL PRIMARY KEY,
    rol ENUM('estudiantes', 'docente') NOT NULL,
    nombres VARCHAR(255),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    contrasena_hash VARCHAR(255) NOT NULL,
    cursando_actualmente BOOLEAN DEFAULT FALSE,
    mail VARCHAR(255) UNIQUE NOT NULL,
    grupo_ID INT
);
CREATE TABLE IF NOT EXISTS grupos (
    grupo_ID INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL
);
ALTER TABLE usuarios ADD FOREIGN KEY (grupo_ID) REFERENCES grupos(grupo_ID) ON DELETE SET NULL;
CREATE TABLE IF NOT EXISTS cursos (
    curso_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_curso VARCHAR(255) NOT NULL,
    descripcion TEXT
);
CREATE TABLE IF NOT EXISTS evaluaciones (
    evaluacion_ID INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(255),
    descripcion VARCHAR(255),
    fecha DATETIME,
    curso_id INT,
    FOREIGN KEY (curso_id) REFERENCES cursos(curso_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS notas (
    alumno_padron INT NOT NULL,
    evaluacion_ID INT NOT NULL,
    nota DECIMAL(5,2),
    PRIMARY KEY (alumno_padron, evaluacion_ID),
    FOREIGN KEY (alumno_padron) REFERENCES usuarios(padron) ON DELETE CASCADE,
    FOREIGN KEY (evaluacion_ID) REFERENCES evaluaciones(evaluacion_ID) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS asistencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asistio BOOLEAN DEFAULT FALSE,
    fecha DATE NOT NULL,
    padron INT NOT NULL,
    justificado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (padron) REFERENCES usuarios(padron) ON DELETE CASCADE
);