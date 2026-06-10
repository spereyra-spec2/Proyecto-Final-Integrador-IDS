DROP DATABASE IF EXISTS ids_db;
CREATE DATABASE ids_db;
USE ids_db;


CREATE TABLE IF NOT EXISTS Curso (
    idCurso INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    codigo VARCHAR(255),
    cuatrimestre VARCHAR(255),
    descripcion VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS Usuarios (
    padron INT PRIMARY KEY NOT NULL,
    rol ENUM('Alumno', 'Docente') NOT NULL,
    nombres VARCHAR(255),
    mail VARCHAR(255) UNIQUE, 
    contrasena_hash VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS Curso_has_Usuarios (
    Curso_idCurso INT NOT NULL,
    Usuarios_padron INT NOT NULL,
    cursando_actualmente TINYINT DEFAULT 1,
    PRIMARY KEY (Curso_idCurso, Usuarios_padron), 
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso) ON DELETE CASCADE,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Asistencias (
    idAsistencia INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    asistio TINYINT DEFAULT 0,
    fecha DATETIME NOT NULL,
    justificado TINYINT DEFAULT 0,
    hash_qr VARCHAR(512),
    Usuarios_padron INT NOT NULL,
    Curso_idCurso INT NOT NULL,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE,
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Equipos (
    idEquipos INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    access_code VARCHAR(255) UNIQUE,
    cupo INT DEFAULT 4,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    Curso_idCurso INT NOT NULL,
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Usuarios_has_Equipos (
    Usuarios_padron INT NOT NULL,
    Equipos_idEquipos INT NOT NULL,
    activo TINYINT DEFAULT 1,
    activo_desde DATETIME,
    activo_hasta DATETIME,
    PRIMARY KEY (Usuarios_padron, Equipos_idEquipos), 
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE,
    FOREIGN KEY (Equipos_idEquipos) REFERENCES Equipos(idEquipos) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Evaluaciones (
    idEvaluacion INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    descripcion VARCHAR(255),
    tipo VARCHAR(255), 
    fecha DATETIME,
    Curso_idCurso INT NOT NULL,
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Equipos_has_Evaluaciones (
    Equipos_idEquipos INT NOT NULL,
    Evaluaciones_idEvaluacion INT NOT NULL,
    PRIMARY KEY (Equipos_idEquipos, Evaluaciones_idEvaluacion), 
    FOREIGN KEY (Equipos_idEquipos) REFERENCES Equipos(idEquipos) ON DELETE CASCADE,
    FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES Evaluaciones(idEvaluacion) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Usuarios_has_Evaluaciones (
    Usuarios_padron INT NOT NULL,
    Evaluaciones_idEvaluacion INT NOT NULL,
    PRIMARY KEY (Usuarios_padron, Evaluaciones_idEvaluacion), 
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE,
    FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES Evaluaciones(idEvaluacion) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Notas (
    idNotas INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    puntaje FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    Evaluaciones_idEvaluacion INT NOT NULL,
    Equipos_idEquipos INT,
    Usuarios_padron INT,   
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE SET NULL, 
    FOREIGN KEY (Equipos_idEquipos) REFERENCES Equipos(idEquipos) ON DELETE CASCADE,
    FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES Evaluaciones(idEvaluacion) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Logs (
    idLogs INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    accion VARCHAR(255),
    Usuarios_padron INT NOT NULL,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE
);