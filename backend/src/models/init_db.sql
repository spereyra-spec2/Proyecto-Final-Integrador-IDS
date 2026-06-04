CREATE DATABASE IF NOT EXISTS ids_db;
USE ids_db;
<<<<<<< HEAD

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
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS Curso_has_Usuarios (
    Curso_idCurso INT NOT NULL,
    Usuarios_padron INT NOT NULL,
    cursando_actualmente TINYINT,
    FOREIGN KEY (Curso_idCurso) REFERENCES Curso(idCurso) ON DELETE CASCADE,
    FOREIGN KEY (Usuarios_padron) REFERENCES Usuarios(padron) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Asistencias (
    idAsistencia INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    asistio TINYINT,
    fecha DATETIME,
    justificado TINYINT,
	hash_qr VARCHAR(512),
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
=======
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
>>>>>>> emanuel_dev
