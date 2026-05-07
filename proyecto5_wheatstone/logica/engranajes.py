# engranajes.py - Lógica del Proyecto 5: Criptógrafo de Wheatstone
#
# Implementa el modelo matemático de los engranajes de Wheatstone:
# - Disco exterior: 27 posiciones (A-Z + _)
# - Disco interior: 26 posiciones (A-Z)
# El desfase entre ellos permite que una misma letra se cifre diferente
# en sucesivas apariciones.

DISCO_EXT = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DISCO_INT = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# DISCO_INT = "QWERTYUIOPASDFGHJKLZXCVBNM"

def normalizar_texto(texto):
    """
    Convierte el texto a mayúsculas, cambia espacios por '_',
    y elimina caracteres que no pertenezcan al alfabeto exterior.
    """
    res = ""
    for char in texto.upper():
        if char == " ":
            char = "_"
        if char in DISCO_EXT:
            if res and res[-1] == char and char in DISCO_INT:
                res += "Q"
            else:
                res += char
    return res

def calcular_avance(pos_actual, char_objetivo, alfabeto):
    """
    Calcula cuántos pasos debe avanzar la aguja desde 'pos_actual'
    hasta encontrar 'char_objetivo' en 'alfabeto', siempre moviéndose hacia adelante.
    Si pos_actual ya apunta a char_objetivo, avanza una vuelta completa (len(alfabeto)).
    """
    idx_objetivo = alfabeto.index(char_objetivo)
    n = len(alfabeto)
    avance = (idx_objetivo - pos_actual) % n
    if avance == 0:
        avance = n  # Nunca se queda en el mismo lugar, da una vuelta entera
    return avance

def cifrar_wheatstone(texto_claro, pos_ext_inicial=0, pos_int_inicial=0):
    """
    Cifra un texto plano usando el mecanismo de Wheatstone.
    Devuelve el texto cifrado y la lista de pasos para la animación.
    """
    texto = normalizar_texto(texto_claro)
    resultado = ""
    pasos = []
    
    pos_ext = pos_ext_inicial
    pos_int = pos_int_inicial
    
    for letra in texto:
        avance = calcular_avance(pos_ext, letra, DISCO_EXT)
        
        pos_ext_nueva = (pos_ext + avance) % 27
        pos_int_nueva = (pos_int + avance) % 26
        
        letra_cifrada = DISCO_INT[pos_int_nueva]
        resultado += letra_cifrada
        
        pasos.append({
            'letra_clara': letra,
            'avance': avance,
            'pos_ext_pre': pos_ext,
            'pos_int_pre': pos_int,
            'pos_ext_post': pos_ext_nueva,
            'pos_int_post': pos_int_nueva,
            'letra_cifrada': letra_cifrada
        })
        
        pos_ext = pos_ext_nueva
        pos_int = pos_int_nueva
        
    return resultado, pasos

def descifrar_wheatstone(texto_cifrado, pos_ext_inicial=0, pos_int_inicial=0):
    """
    Descifra un texto usando el mecanismo de Wheatstone.
    El proceso es inverso: se busca la letra cifrada en el disco interior,
    se avanza ambas agujas esa cantidad, y se lee el disco exterior.
    Devuelve el texto claro y los pasos de la animación.
    """
    # El texto cifrado solo debe contener A-Z
    texto = "".join(c for c in texto_cifrado.upper() if c in DISCO_INT)
    resultado = ""
    pasos = []
    
    pos_ext = pos_ext_inicial
    pos_int = pos_int_inicial
    
    for letra_cifrada in texto:
        avance = calcular_avance(pos_int, letra_cifrada, DISCO_INT)
        
        pos_ext_nueva = (pos_ext + avance) % 27
        pos_int_nueva = (pos_int + avance) % 26
        
        letra_clara = DISCO_EXT[pos_ext_nueva]
        resultado += letra_clara
        
        pasos.append({
            'letra_cifrada': letra_cifrada,
            'avance': avance,
            'pos_ext_pre': pos_ext,
            'pos_int_pre': pos_int,
            'pos_ext_post': pos_ext_nueva,
            'pos_int_post': pos_int_nueva,
            'letra_clara': letra_clara
        })
        
        pos_ext = pos_ext_nueva
        pos_int = pos_int_nueva
        
    return resultado, pasos

def simular_caso_aaaa():
    """
    Demostración de que letras idénticas se cifran distinto (ej. AAAA).
    Retorna el texto cifrado resultante.
    """
    res, _ = cifrar_wheatstone("AAAA", 0, 0)
    return res

def simular_caso_espacio():
    """
    Demostración de cómo el espacio cambia el alfabeto interno (ej. HOLA MUNDO).
    """
    res, _ = cifrar_wheatstone("HOLA MUNDO", 0, 0)
    return res
