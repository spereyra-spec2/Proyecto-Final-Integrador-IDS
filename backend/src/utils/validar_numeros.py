def valido_numero(numero):
    try:
        if numero > 0 and isinstance(numero, int):
            return True
        return False
    except ValueError:
        return False

    