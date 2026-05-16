CREATE DATABASE IF NOT EXISTS ids_db;
USE ids_db;

CREATE TABLE IF NOT EXISTS usuarios (
	id_usuario INT NOT NULL PRIMARY KEY,
	rol ENUM('Alumno', 'Docente'),
	nombres VARCHAR(255),
	fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
	contrasena_hash VARCHAR(255),
	mail VARCHAR(255) UNIQUE,
);

CREATE TABLE IF NOT EXISTS alumno (
	id_alumno INT NOT NULL,
	padron INT NOT NULL UNIQUE PRIMARY KEY,
	cursando BOOLEAN DEFAULT TRUE,
	grupo_ID INT,
	FOREIGN KEY (id_alumno) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
	FOREIGN KEY (grupo_ID) REFERENCES grupos(grupo_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS docente (
	id_docente INT NOT NULL,
	padron INT NOT NULL UNIQUE PRIMARY KEY,
	FOREIGN KEY (id_docente) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS grupos (
	nombre VARCHAR(255),
	grupo_ID INT AUTO_INCREMENT PRIMARY KEY,
	evaluacion_ID INT,
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
	alumno_padron INT,
	grupo_ID INT,
	evaluacion_ID INT,
	nota DECIMAL(5,2),
	FOREIGN KEY (alumno_padron) REFERENCES usuarios(padron),
	FOREIGN KEY (grupo_ID) REFERENCES grupos(grupo_ID),
	FOREIGN KEY (evaluacion_ID) REFERENCES evaluaciones(evaluacion_ID)
);


