def valido_numero(numero):
    try:
        if int(numero) > 0:
            return True
        return False
    
    except ValueError:
        return False

    