# Validar el dominio del email
def validar_email_fiuba(email):
    """
    Valida que el email contenga un '@', tenga texto antes del '@' 
    y el dominio sea exactamente 'fi.uba.ar'.
    """
    usuario = ""
    dominio = ""
    
    if email and '@' in email:
        partes = email.rsplit('@', 1)
        usuario = partes[0].strip()
        dominio = partes[1].strip()
        
    return usuario != '' and dominio == 'fi.uba.ar'
