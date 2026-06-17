# Proyecto-Final-Integrador-IDS — Plataforma Web de Gestión Académica
En este proyecto trabajaremos en el TFI de la materia Introducción al Desarrollo de Software cátedra Lanzillota primer cuatrimestre - 2026

Equipo: Los Punto y Coma

> **Aviso:** este proyecto es **código de ejemplo** con fines didácticos. Puede contener errores, simplificaciones o decisiones de diseño discutibles. Si se usa como base para un trabajo práctico u otro entregable, **debe adaptarse a las buenas prácticas y consignas específicas de la materia/cátedra** (estilo de código, manejo de errores, validaciones, tests, estructura, etc.).

## Motivación

**AcademiQ** es una aplicación full-stack diseñada para la administración y control integral de cursos universitarios conforme a los lineamientos del proyecto final de la cátedra. Su **objetivo pedagógico** es ilustrar cómo estructurar una aplicación escalable dividida en dos capas independientes: un **Backend (API)** de servicios puros y un **Frontend (Web)** que aplica Renderizado del Lado del Servidor (SSR), interactuando mediante transferencia de datos JSON y persistencia en una base de datos relacional **MySQL**.

A diferencia de soluciones monolíticas básicas, este desarrollo aborda de forma explícita los requerimientos de la consigna:
- **Seguridad perimetral:** Autenticación robusta y control de acceso basado en roles para Docentes y Alumnos.
- **Auditoría del sistema:** Registro centralizado de logs para el control de actividad e integridad de datos.
- **Automación de procesos:** Carga masiva de estudiantes por archivos estructurados CSV, generación automática de reportes ejecutivos en PDF y un módulo de control de presencias mediante códigos QR dinámicos.

## Arquitectura

           Browser
              |
              v 
     Peticiones HTTP & Formularios Web 
     
     Frontend Web (Flask Server, Puerto 5001) 
              |
              v 
    (API Calls / JSON / Cabecera Authorization Bearer Token) 
    Backend API  (Flask REST API, Puerto 5000) 
              |
              v 
    (Consultas SQL con mysql-connector) 
     Base de Datos (MySQL - Esquema ids_db) 


No hay lógica compartida en memoria entre capas; el Frontend es estrictamente un cliente HTTP de la API Backend.

## Estructura del proyecto

```text
Proyecto-AcademiQ/
├── backend/                            # Capa de lógica de negocio y servicios API (Puerto 5000)
│   ├── app.py                          # Entry point de la API REST
│   ├── config.py                       # Parámetros del entorno y credenciales de base de datos
│   ├── datos_de_prueba.py              # Script utilitario para poblar la DB con datos iniciales
│   ├── mail.py                         # Configuración y utilitarios para notificaciones de e-mail
│   ├── qr_asistencia.png               # Imagen del código QR dinámico de presencias
│   └── src/
│       ├── db/                         # Persistencia de datos relacional
│       │   ├── db.py                   # Context manager y pools de conexión MySQL
│       │   ├── ev_notas_db.py          # Consultas para rúbricas, evaluaciones y notas
│       │   ├── init_db.py              # Script automatizado para la creación de esquemas
│       │   └── init_db.sql             # Script SQL con definiciones físicas de tablas DDL
│       ├── routes/                     # Capa de control organizada por Blueprints (API)
│       │   ├── alumnos.py              # Endpoints para inscripción, modificación y baja de alumnos
│       │   ├── api_ev_notas.py         # Endpoints para asignación y consulta de calificaciones
│       │   ├── asistencia.py           # Endpoints de control diario de asistencia y QR
│       │   ├── auth/                   # Módulo aislado de control de accesos
│       │   │   ├── auth.py             # Rutas API de registro, login y tokens
│       │   │   └── auth_db.py          # Consultas y validaciones criptográficas de usuarios
│       │   ├── cursos.py               # Gestión de comisiones académicas
│       │   ├── equipos.py              # Gestión de grupos y códigos de acceso
│       │   └── evaluaciones.py         # Definición de instrumentos (Parciales, TPs, etc.)
│       └── utils/                      # Librerías auxiliares y de seguridad
│           ├── archivo_de_prueba.csv   # Dataset de muestra para pruebas de carga masiva
│           ├── asistencia_utils.py     # Lógica de codificación matemática para asistencia
│           ├── errors.py               # Mapeo semántico de códigos de error HTTP
│           ├── funciones.py            # Helpers globales de auditoría, JWT y verificación segura
│           ├── seguridad.py            # Hashing e inspección criptográfica de contraseñas
│           ├── validaciones.py         # Reglas de negocio duras (Padrón 6 dígitos y email)
│           └── validar_numeros.py      # Filtros de sanitización matemática frente a inyecciones
├── docs/                               # Repositorio de requerimientos y diseño
│   ├── endpoints_a_desarrollar.txt     # Matriz de cobertura técnica del Backend
│   ├── endpoints.pdf                   # Especificaciones de contratos y payloads JSON
│   ├── mockup.txt                      # Wireframes estructurales en modo texto
│   └── Proyecto Final IDS 2026C1 .pdf  # Enunciado y directivas oficiales de la cátedra
├── frontend/                           # Capa de interacción con el usuario (Puerto 5001)
│   ├── app.py                          # Entry point del servidor web SSR
│   ├── constants.py                    # Constantes del entorno global web
│   ├── src/
│   │   ├── routes/                     # Controladores de rutas Flask Web (Vistas HTML)
│   │   │   ├── alumno.py               # Rutas privadas para el rol Alumno
│   │   │   ├── asistencias.py          # Orquestación de pantallas de asistencia
│   │   │   ├── auth.py                 # Pantallas de login, registro y restauración
│   │   │   ├── equipos.py              # Vistas de conformación grupal por alumnos
│   │   │   └── profesor.py             # Dashboard del docente, ABMs y reportes PDF
│   │   └── services/                   # Clientes HTTP encargados de delegar hacia la API
│   │   │   ├── alumnos.py              # Consumo de rutas de alumnos y CSV multipart
│   │   │   ├── auth.py                 # Negociación de sesiones y validación de tokens
│   │   │   ├── cursos.py               # Cliente HTTP para gestión de comisiones
│   │   │   ├── equipos.py              # Gestión de grupos de trabajo
│   │   │   ├── evaluaciones.py         # Cliente HTTP para instrumentos de evaluación
│   │   │   └── ev_notas_service.py     # Servicios de interacción de calificaciones
│   ├── static/                         # Recursos estáticos del frontend
│   │   ├── css/                        # Estilos CSS segmentados de forma modular
│   │   └── js/                         # Lógica dinámica del cliente (Validaciones frontend)
│   └── templates/                      # Archivos de la vista renderizados mediante Jinja2
└── requirements.txt                    # Listado único de dependencias del ecosistema
```

## Requisitos previos
Python 3.12+
Motor de Base de Datos MySQL activo (Puerto por defecto: 3306).

## Instalación y ejecución
**1. Inicialización de la Base de Datos**
Crea la base de datos ids_db e inserta la estructura de tablas relacionales ejecutando el script provisto:
bash: 
mysql -u tu_usuario -p < backend/src/db/init_db.sql

**2. Despliegue del Backend (API REST)**
Accede a la carpeta de backend, crea un entorno virtual aislado, instala las dependencias y arranca el microservicio:
bash: 
cd backend
python -m venv venv
#Activar en Windows
venv\Scripts\activate
#Activar en Linux/macOS
source venv/bin/activate
en el archio	
rellenar las variables de "password" y "SECRET_KEY" con la informacion acorde

**3. Despliegue del Frontend (Web Server)**
Abre una terminal paralela, accede a la carpeta del frontend, inicializa su respectivo entorno e inicia el servidor web:
bash: 
cd frontend
python -m venv venv

#Activar en Windows
venv\Scripts\activate
#Activar en Linux/macOS
source venv/bin/activate

**4. Instalación de dependecias** <br>

**Caso linux** <br>
una vez instalado e iniciado en entorno virtual, instalar las dependencias con:
	chmod +x instalacion.sh
	./instalacion.sh



Gestión de Alumnos: Páginas y Flujos

El sistema de gestión de alumnos es operado por el personal docente a través de llamadas asincrónicas delegadas a la API, respetando las restricciones de integridad.

### Matriz de Rutas Web de Alumnos (Panel de Profesores)

| Ruta Web (Frontend) | Método | Login Requerido | Descripción |
|---------------------|--------|-----------------|-------------|
| `/cursos/<id>/alumnos` | `GET` | Sí (Docente) | Grilla con el padrón general de alumnos inscriptos con filtros nativos por estado. |
| `/cursos/<id>/alumnos/inscribir` | `POST` | Sí (Docente) | Envío del formulario de alta manual para un nuevo estudiante. |
| `/cursos/<id>/alumnos/importar` | `POST` | Sí (Docente) | Carga y procesamiento masivo de datos mediante archivo `.csv` adjunto. |
| `/cursos/<id>/alumnos/actualizar/<p>`| `POST` | Sí (Docente) | Actualización de datos filiatorios o flag de deserción del alumno en la comisión. |
| `/cursos/<id>/alumnos/baja-logica/<p>`| `POST` | Sí (Docente) | Ejecuta el procesamiento de baja lógica de un alumno en un curso específico. |
| `/cursos/<id>/alumnos/ficha/<p>` | `GET` | Sí (Docente) | Ficha consolidada del estudiante: despliega datos, notas y asistencias del curso. |

### Flujos Principales de Operación

#### Alta Manual e Importación Masiva

1. Al agregar un alumno manual (`/inscribir`), el Frontend captura las variables y el JavaScript realiza una validación preventiva.

2. Si los datos respetan los formatos, se dispara una petición `POST` a la API. Esta verifica la disponibilidad de claves únicas en la tabla `Usuarios` (padrón y mail). Si existe conflicto, aborta de forma segura devolviendo un estado HTTP `409 Conflict`.

3. Para la importación, el docente selecciona un archivo delimitado por comas. El Frontend delega el archivo por streaming multipart a la API, la cual procesa línea por línea mediante `executemany` utilizando cláusulas `ON DUPLICATE KEY UPDATE` e `INSERT IGNORE` para evitar colisiones catastróficas.

#### Baja Lógica y Control de Continuidad

1. El borrado físico de registros académicos está estrictamente prohibido por reglas de auditoría. Al pulsar el botón de eliminación, se desencadena una petición hacia el endpoint `DELETE` de la API.

2. El sistema actualiza la relación intermedia cambiando el atributo `Curso_has_Usuarios.Estado = 0`.

3. Inmediatamente después, el backend ejecuta un conteo de control: si el alumno evaluado no posee ninguna otra materia con `Estado = 1` en toda la institución, el sistema apaga su flag global actualizando la tabla a `Usuarios.cursando_actualmente = 0` y registrando el evento en el Log de auditoría.

#### Control de Asistencia mediante Código QR Dinámico

1. **Generación del Código Criptográfico:** El docente inicia el flujo desde la interfaz general de asistencias. El Frontend delega la acción al Backend consumiendo el endpoint `GET /generar-qr`. La API codifica un diccionario que contiene la acción académica y la fecha ISO actual, firmándolo criptográficamente mediante `URLSafeTimedSerializer`.

2. **Generación de la Imagen:** La URL resultante codifica el acceso al formulario web público de registro. El backend dibuja la matriz bidimensional usando la librería `qrcode` y almacena localmente el recurso estático para servirlo a través de un flujo estructurado de archivos.

3. **Validación de Expiración en Aula:** Cuando el alumno escanea el código con su dispositivo móvil e ingresa su padrón, el Frontend transmite los parámetros por JSON al backend. La API procesa el descifrado del token controlando el ciclo de vigencia mediante el parámetro de tiempo configurado.

4. **Validación de Doble Firma:** Si el token no sufrió adulteraciones (`BadSignature`) ni excedió el tiempo límite en el aula (`SignatureExpired`), el backend comprueba la existencia de la cuenta y consulta el estado diario de firmas. Si ya se registró una presencia para ese padrón en la fecha actual, se aborta la transacción devolviendo un estado HTTP `409 Conflict`.

## Reglas de Validación de Negocio

El ecosistema cuenta con un set de políticas restrictivas en la capa de utilitarios (`backend/src/utils/validaciones.py`):
- **Estructura Crítica de Padrón:** Debe ser exclusivamente un número entero positivo de exactamente **6 dígitos** (rango válido: `100000` a `999999`). Se bloquean de forma nativa entradas alfabéticas, longitudes parciales o valores que comiencen con el dígito cero.

- **Filtro de Email FIUBA:** Se audita mediante expresiones regulares que la dirección del correo ingresado finalice de manera estricta en el dominio institucional de la facultad (`@fi.uba.ar`). Ningún dominio comercial o externo es aceptado.

## Control de Errores y Notificaciones

El sistema cuenta con un circuito de notificaciones unificado para asegurar la correcta comunicación de incidentes académicos:
- **Validación en Cliente en Tiempo Real:** El HTML de las plantillas (`profesor-alumnos.html`) restringe de forma nativa la longitud de los inputs. Adicionalmente, el JavaScript (`static/js/profesor.js`) sanitiza en tiempo real las pulsaciones del teclado eliminando letras en campos numéricos y evaluando la terminación del correo mediante `setCustomValidity`, bloqueando el envío erróneo antes de que viaje la petición por la red.

- **Manejo de Errores en Servidor (Flask Flash):** Si una regla es vulnerada en el Backend, la API retorna códigos de error HTTP estructurados. Las rutas del Frontend interceptan el payload, extraen de forma segura las descripciones y las inyectan en la interfaz del usuario final utilizando **Mensajes Flash**, desplegando banners dinámicos de éxito o error sobre el layout común.

- **Políticas de Resiliencia ante Caídas:** Si el microservicio de la API backend se encuentra inactivo, las llamadas HTTP encapsuladas en `services/` capturan la excepción `ConnectionError` y devuelven una interfaz controlada indicando que el canal de comunicación requiere supervisión, protegiendo al servidor web de colapsos inesperados.

## Glosario de Términos

- **Flask:** Microframework web en Python utilizado para construir tanto la API de datos como el servidor de interfaz web de este proyecto.

- **Jinja2:** Motor de plantillas que utiliza Flask para renderizar HTML dinámico en el servidor (SSR) inyectando datos directamente en los componentes visuales.

- **Template Base (`base.html` / `base_profesores.html`):** Plantilla estructural que define la anatomía común del sitio de la cual heredan las demás páginas mediante la instrucción `{% extends %}`.

- **`{% block %}`:** Directiva del motor de plantillas que delimita áreas específicas del layout padre diseñadas para ser reescritas por vistas hijas (ej. títulos o scripts).

- **Blueprint (Flask):** Herramienta que permite organizar y segregar de manera modular conjuntos de rutas web o endpoints relacionados en archivos independientes de la aplicación.

- **Service:** Capa encargada de aislar el consumo de recursos externos. En el Frontend, realiza las llamadas HTTP estructuadas mediante la librería `requests` apuntando hacia el Backend.

- **JWT (JSON Web Token):** Token firmado digitalmente que la API entrega tras un inicio de sesión exitoso y que sirve para autorizar peticiones subsiguientes.

- **`flask.session`:** Cookie firmada criptográficamente del lado del servidor que almacena la información básica del usuario logueado y su correspondiente token JWT, protegiendo los datos frente a ataques de inyección JavaScript de tipo XSS.

- **Flash Messages:** Mensajes efímeros de lectura única que viajan entre redirecciones Flask, utilizados para confirmar éxitos operativos o advertir fallos críticos.

- **Baja Lógica:** Técnica que consiste en deshabilitar la vigencia de un registro cambiando una bandera de estado en lugar de remover físicamente la fila, preservando la coherencia referencial.

- **Auditoría (Log):** Tabla dedicada a capturar de manera secuencial cada acción administrativa llevada a cabo por un operador identificado para garantizar la trazabilidad de los datos académicos.

- **ReportLab:** Librería de Python integrada en el backend para la exportación y dibujo estructurado en formato PDF de listados, aprobaciones y estadísticas.

- **QRCode:** Componente de software encargado de transformar variables temporales cifradas en matrices bidimensionales (imágenes QR) para agilizar los procesos de asistencia en el aula.}


- **Entorno Virtual (venv):** Directorio aislado del sistema operativo diseñado para empaquetar de manera estricta las versiones exactas de las librerías declaradas en el archivo `requirements.txt`.
