CREATE DATABASE IF NOT EXISTS ids_db;
USE ids_db;

CREATE TABLE IF NOT EXISTS usuarios (
	padron INT NOT NULL PRIMARY KEY,
	rol ENUM('estudiantes', 'docente'),
	nombres VARCHAR(255),
	fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
	contrasena_hash VARCHAR(255),
	cursando_actualmente BOOLEAN,
	mail VARCHAR(255) UNIQUE,
	grupo_ID INT,
	FOREIGN KEY (grupo_ID) REFERENCES grupos(grupo_ID) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS grupos (
	nombre VARCHAR(255),
	grupo_ID INT AUTO_INCREMENT PRIMARY KEY,
	FOREIGN KEY (evaluacion_ID) REFERENCES evaluaciones(evaluacion_ID)
);

CREATE TABLE IF NOT EXISTS evaluaciones (
	evaluacion_ID INT AUTO_INCREMENT PRIMARY KEY,
	tipo ENUM('parcial', 'parcialito', 'TP', 'final'),
	instancia INT,
	tema INT,
	fecha DATETIME
);

CREATE TABLE IF NOT EXISTS notas (
	alumno_padron INT NOT NULL,
	grupo_ID INT,
	evaluacion_ID INT,
	nota DECIMAL(5,2),
	FOREIGN KEY (alumno_padron) REFERENCES usuarios(padron),
	FOREIGN KEY (grupo_ID) REFERENCES grupos(grupo_ID),
	FOREIGN KEY (evaluacion_ID) REFERENCES evaluaciones(evaluacion_ID),
);

CREATE TABLE IF NOT EXISTS asistencias (
	asistio BOOLEAN,
	fecha DATE,
	padron INT,
	justificado BOOLEAN,
	FOREIGN KEY (padron) REFERENCES usuarios(padron)
);
