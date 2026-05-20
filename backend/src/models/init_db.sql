CREATE DATABASE IF NOT EXISTS ids_db;
USE ids_db;

CREATE TABLE IF NOT EXISTS cursos (
	curso_ID INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(255)
);	

CREATE TABLE IF NOT EXISTS evaluaciones (
	evaluacion_ID INT AUTO_INCREMENT PRIMARY KEY,
	tipo ENUM('parcial', 'parcialito', 'TP', 'final'),
	instancia INT,
	tema INT,
	fecha DATETIME
);

CREATE TABLE IF NOT EXISTS grupos (
	grupo_ID INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(255),
	evaluacion_ID INT,
	curso_ID INT NOT NULL,
	FOREIGN KEY (evaluacion_ID) REFERENCES evaluaciones(evaluacion_ID) ON DELETE SET NULL,
	FOREIGN KEY (curso_ID) REFERENCES cursos(curso_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS usuarios (
	padron INT NOT NULL PRIMARY KEY,
	rol ENUM('estudiantes', 'docente') NOT NULL,
	nombres VARCHAR(255) NOT NULL,
	fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
	contrasena_hash VARCHAR(255),
	cursando_actualmente BOOLEAN DEFAULT TRUE,
	mail VARCHAR(255) UNIQUE NOT NULL,
	curso_ID INT,
	grupo_ID INT,
	FOREIGN KEY (curso_ID) REFERENCES cursos(curso_ID) ON DELETE SET NULL,
	FOREIGN KEY (grupo_ID) REFERENCES grupos(grupo_ID) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notas (
	alumno_padron INT NOT NULL,
	grupo_ID INT,
	evaluacion_ID INT NOT NULL,
	nota DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (alumno_padron, evaluacion_ID),
	FOREIGN KEY (alumno_padron) REFERENCES usuarios(padron) ON DELETE CASCADE,
	FOREIGN KEY (grupo_ID) REFERENCES grupos(grupo_ID) ON DELETE SET NULL,
	FOREIGN KEY (evaluacion_ID) REFERENCES evaluaciones(evaluacion_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS asistencias (
	asistio BOOLEAN,
	fecha DATE,
	padron INT,
	justificado BOOLEAN DEFAULT FALSE,
	curso_ID INT,
	FOREIGN KEY (padron) REFERENCES usuarios(padron) ON DELETE CASCADE,
	FOREIGN KEY (curso_ID) REFERENCES cursos(curso_ID) ON DELETE CASCADE
);