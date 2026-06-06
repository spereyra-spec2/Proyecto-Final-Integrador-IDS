import re

def es_email_valido(mail):
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(patron, mail):
        return True
    return False

def validar_curso_id(curso_id):
    try:
        curso_id = int(curso_id)
    except ValueError:
        raise ValueError("El ID del curso debe ser numérico")

    if curso_id <= 0:
        raise ValueError("El ID del curso debe ser positivo")

    return curso_id


def validar_padron(padron):
    try:
        padron = int(padron)
    except ValueError:
        raise ValueError("El padrón debe ser numérico")

    if padron <= 0:
        raise ValueError("El padrón debe ser positivo")

    return padron