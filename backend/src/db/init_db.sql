CREATE DATABASE IF NOT EXISTS ids_db;
USE ids_db;

CREATE TABLE IF NOT EXISTS Curso (
    idCurso INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    descripcion VARCHAR(255),
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS Usuarios (
    padron INT PRIMARY KEY NOT NULL,
    rol ENUM('Alumno', 'Docente'),
    nombres VARCHAR(255),
    mail VARCHAR(255),
    contrasena_hash VARCHAR(255),
    cursando_actualmente TINYINT,
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS Curso_has_Usuarios (
    Curso_idCurso INT NOT NULL,
    Usuarios_padron INT NOT NULL,
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso) ON DELETE CASCADE,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Asistencias (
    idAsistencia INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    asistio TINYINT,
    fecha DATETIME,
    justificado TINYINT,
    Usuarios_padron INT NOT NULL,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Equipos (
    idEquipos INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(255),
    created_at DATETIME,
    Curso_idCurso INT NOT NULL,
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Usuarios_has_Equipos (
    Usuarios_padron INT NOT NULL,
    Equipos_idEquipos INT NOT NULL,
    activo TINYINT,
    activo_desde DATETIME,
    activo_hasta DATETIME,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron),
    FOREIGN KEY (Equipos_idEquipos) REFERENCES Equipos(idEquipos)
);

CREATE TABLE IF NOT EXISTS Evaluaciones (
    idEvaluacion INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    descripcion VARCHAR(255),
    tipo VARCHAR(255),
    fecha DATETIME,
    instancia INT,
    Curso_idCurso INT NOT NULL,
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso)
);

CREATE TABLE IF NOT EXISTS Equipos_has_Evaluaciones (
    Equipos_idEquipos INT NOT NULL,
    Evaluaciones_idEvaluacion INT NOT NULL,
    FOREIGN KEY (Equipos_idEquipos) REFERENCES Equipos(idEquipos),
    FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES Evaluaciones(idEvaluacion)
);

CREATE TABLE IF NOT EXISTS Usuarios_has_Evaluaciones (
    Usuarios_padron INT NOT NULL,
    Evaluaciones_idEvaluacion INT NOT NULL,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron),
    FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES Evaluaciones(idEvaluacion)
);

CREATE TABLE IF NOT EXISTS Notas (
    idNotas INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    puntaje FLOAT,
    created_at DATETIME,
    Evaluaciones_idEvaluacion INT NOT NULL,
    Equipos_idEquipos INT,
    Usuarios_padron INT,   
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron),
    FOREIGN KEY (Equipos_idEquipos) REFERENCES Equipos(idEquipos),
    FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES Evaluaciones(idEvaluacion)
);

CREATE TABLE IF NOT EXISTS Logs (
    idLogs INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    fecha DATETIME,
    accion VARCHAR(255),
    Usuarios_padron INT NOT NULL,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron)
);

