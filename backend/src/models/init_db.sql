CREATE DATABASE IF NOT EXISTS ids_db;
USE ids_db;

CREATE TABLE IF NOT EXISTS curso (
                                     idCurso INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                                     nombre VARCHAR(255),
                                     descripcion VARCHAR(255),
                                     created_at DATETIME
);

CREATE TABLE IF NOT EXISTS usuarios (
                                        padron INT PRIMARY KEY NOT NULL,
                                        rol ENUM('Alumno', 'Docente'),
                                        nombres VARCHAR(255),
                                        mail VARCHAR(255),
                                        contrasena_hash VARCHAR(255),
                                        cursando_actualmente TINYINT,
                                        created_at DATETIME
);

CREATE TABLE IF NOT EXISTS curso_has_usuarios (
                                                  curso_idcurso INT NOT NULL,
                                                  usuarios_padron INT NOT NULL,
                                                  FOREIGN KEY (curso_idCurso) REFERENCES curso(idcurso) ON DELETE CASCADE,
                                                  FOREIGN KEY (usuarios_padron) REFERENCES usuarios(padron) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS asistencias (
                                           idAsistencia INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                                           asistio TINYINT,
                                           fecha DATETIME,
                                           justificado TINYINT,
                                           usuarios_padron INT NOT NULL,
                                           FOREIGN KEY (usuarios_padron) REFERENCES usuarios(padron) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS equipos (
                                       idEquipos INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                                       nombre VARCHAR(255),
                                       created_at DATETIME,
                                       curso_idcurso INT NOT NULL,
                                       FOREIGN KEY (curso_idcurso) REFERENCES curso(idCurso) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS usuarios_has_equipos (
                                                    usuarios_padron INT NOT NULL,
                                                    equipos_idequipos INT NOT NULL,
                                                    activo TINYINT,
                                                    activo_desde DATETIME,
                                                    activo_hasta DATETIME,
                                                    FOREIGN KEY (usuarios_padron) REFERENCES usuarios(padron),
                                                    FOREIGN KEY (equipos_idequipos) REFERENCES equipos(idequipos)
);

CREATE TABLE IF NOT EXISTS evaluaciones (
                                            id_evaluacion INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                                            descripcion VARCHAR(255),
                                            tipo VARCHAR(255),
                                            fecha DATETIME,
                                            instancia INT,
                                            curso_idcurso INT NOT NULL,
                                            FOREIGN KEY (curso_idcurso) REFERENCES curso(idCurso)
);

CREATE TABLE IF NOT EXISTS equipos_has_evaluaciones (
                                                        Equipos_idEquipos INT NOT NULL,
                                                        Evaluaciones_idEvaluacion INT NOT NULL,
                                                        FOREIGN KEY (Equipos_idEquipos) REFERENCES equipos(idEquipos),
                                                        FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES evaluaciones(id_evaluacion)
);

CREATE TABLE IF NOT EXISTS usuarios_has_evaluaciones (
                                                         Usuarios_padron INT NOT NULL,
                                                         Evaluaciones_idEvaluacion INT NOT NULL,
                                                         FOREIGN KEY (Usuarios_padron) REFERENCES usuarios(padron),
                                                         FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES evaluaciones(id_evaluacion)
);

CREATE TABLE IF NOT EXISTS notas (
                                     idNotas INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                                     puntaje FLOAT,
                                     created_at DATETIME,
                                     Evaluaciones_idEvaluacion INT NOT NULL,
                                     Equipos_idEquipos INT,
                                     Usuarios_padron INT,
                                     FOREIGN KEY (Usuarios_padron) REFERENCES usuarios(padron),
                                     FOREIGN KEY (Equipos_idEquipos) REFERENCES equipos(idEquipos),
                                     FOREIGN KEY (Evaluaciones_idEvaluacion) REFERENCES evaluaciones(id_Evaluacion)
);

CREATE TABLE IF NOT EXISTS logs (
                                    idLogs INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                                    fecha DATETIME,
                                    accion VARCHAR(255),
                                    Usuarios_padron INT NOT NULL,
                                    FOREIGN KEY (Usuarios_padron) REFERENCES usuarios(padron)
);

