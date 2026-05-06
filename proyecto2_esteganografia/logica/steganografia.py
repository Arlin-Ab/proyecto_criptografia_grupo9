# steganografia.py - Lógica del Proyecto 2: Esteganografía con Rejilla de Cardano
#
# La esteganografía oculta la EXISTENCIA del mensaje, no solo su contenido.
# La rejilla marca qué posiciones del texto de cobertura contienen el mensaje secreto.
# El resto del texto parece inocente y natural.

import random
import json

# ──────────────────────────────────────────────────────────────
# Recursos lingüísticos para generar texto de cobertura en español
# ──────────────────────────────────────────────────────────────

# Palabras cortas comunes en español (para relleno automático)
PALABRAS_RELLENO = [
    "el", "la", "de", "que", "en", "un", "al", "lo", "se", "no",
    "su", "me", "te", "mi", "ya", "si", "hay", "con", "por", "una",
    "era", "muy", "sin", "vez", "los", "las", "del", "mas", "tan",
    "ser", "ver", "dar", "fue", "han", "van", "nos", "son", "hay",
    "esa", "ese", "eso", "ahi", "aun", "bien", "cada", "caso", "como",
    "cosa", "cree", "cual", "dado", "deja", "dias", "dijo", "ella",
    "ellos", "esto", "gran", "hizo", "hora", "iban", "igual", "lado",
    "luego", "lugar", "mas", "mejor", "mismo", "modo", "mucho", "nada",
    "nadie", "nuevo", "obra", "otro", "parte", "pero", "poco", "puede",
    "sabia", "sigue", "sobre", "solo", "tanto", "tengo", "toda", "todo",
    "tres", "tuvieron", "usted", "viene", "vida", "visto", "volvio",
    "agua", "amor", "anoche", "antes", "aqui", "ayer", "busca", "campo",
    "carta", "cerca", "ciudad", "claro", "cosas", "creen", "cuanto",
    "debajo", "dentro", "donde", "entre", "fecha", "finca", "fuera",
    "gente", "hasta", "hecho", "horas", "igual", "joven", "largo",
    "libro", "llega", "lleva", "madre", "manos", "marzo", "media",
    "menos", "mientras", "mismo", "noche", "norte", "nunca", "padre",
    "pared", "patio", "plaza", "poder", "pronto", "pueda", "puerta",
    "queda", "quien", "quiso", "razon", "recibe", "resto", "ronda",
    "salir", "saben", "segun", "semana", "siempre", "tarde", "tiene",
    "tierra", "todos", "tomar", "torno", "trabajo", "trajo", "turno",
    "veces", "venia", "veras", "viaje", "viene", "vista", "vivir",
]

# Distribución de letras frecuentes en español (para relleno más natural)
_POOL_LETRAS = (
    "A" * 13 + "B" * 2 + "C" * 4 + "D" * 5 + "E" * 13 +
    "F" * 1 + "G" * 1 + "H" * 1 + "I" * 7 + "J" * 1 +
    "L" * 5 + "M" * 3 + "N" * 7 + "O" * 9 + "P" * 3 +
    "Q" * 1 + "R" * 7 + "S" * 8 + "T" * 5 + "U" * 4 +
    "V" * 1 + "X" * 1 + "Y" * 1 + "Z" * 1
)

# Sílabas comunes en español para textos más naturales
SILABAS = [
    "LA", "EL", "DE", "EN", "UN", "AL", "LO", "LE", "ME", "SE",
    "NO", "HA", "SU", "TE", "NA", "MA", "CA", "RA", "PA", "TA",
    "SA", "DA", "RE", "CO", "MI", "TO", "RO", "MO", "VE", "LI",
    "NI", "BA", "DI", "FI", "GU", "JU", "LU", "MU", "NU", "PI",
    "RI", "TI", "VI", "ES", "COM", "CON", "POR", "PAR", "TEN",
    "SER", "VER", "MAS", "ERA", "UNA", "TRA", "PRE", "PRO",
    "DES", "BRA", "CLA", "FRA", "GRA", "PLA", "TRA", "CRE",
    "QUE", "IEN", "IER", "IEN", "ION", "ADA", "ANO", "ENO",
]


# ──────────────────────────────────────────────────────────────
# Funciones auxiliares
# ──────────────────────────────────────────────────────────────

def obtener_posiciones_lineales(huecos, n):
    """
    Convierte el conjunto de celdas-hueco (fila, col) a una lista
    de índices lineales ordenados (0-indexed, lectura izquierda-derecha).
    """
    return sorted(fila * n + col for fila, col in huecos)


def rotar_huecos_90(huecos, n):
    """Rota los huecos 90° en sentido horario."""
    return {(col, n - 1 - fila) for fila, col in huecos}


def obtener_todas_rotaciones(huecos, n):
    """Devuelve los 4 conjuntos de huecos (0°, 90°, 180°, 270°)."""
    rots = [huecos]
    actual = huecos
    for _ in range(3):
        actual = rotar_huecos_90(actual, n)
        rots.append(actual)
    return rots


def validar_rejilla(huecos, n):
    """Valida que la rejilla sea matemáticamente correcta."""
    if not huecos:
        return False, "La rejilla no tiene huecos."

    total = n * n
    if total % 4 != 0:
        return False, f"La cuadrícula {n}×{n} no es válida (no divisible entre 4)."

    esperados = total // 4
    if len(huecos) != esperados:
        return False, (
            f"Se necesitan {esperados} huecos para una rejilla {n}×{n}, "
            f"pero hay {len(huecos)}."
        )

    rotaciones = obtener_todas_rotaciones(huecos, n)
    todas = []
    for r in rotaciones:
        todas.extend(r)

    if len(todas) != len(set(todas)):
        return False, "Las rotaciones se superponen. Elige otros huecos."

    if len(set(todas)) != total:
        return False, "Las rotaciones no cubren todas las celdas."

    return True, ""


def generar_rejilla_valida(n):
    """Genera automáticamente una rejilla válida para tamaño n×n."""
    huecos = set()
    visitadas = set()
    for fila in range(n):
        for col in range(n):
            if (fila, col) not in visitadas:
                celda = (fila, col)
                grupo = [celda]
                actual = celda
                for _ in range(3):
                    actual = (actual[1], n - 1 - actual[0])
                    grupo.append(actual)
                grupo_set = set(grupo)
                if len(grupo_set) == 4 and not grupo_set.intersection(visitadas):
                    huecos.add(random.choice(grupo))
                    visitadas.update(grupo_set)
    return huecos


# ──────────────────────────────────────────────────────────────
# Generador de texto de cobertura
# ──────────────────────────────────────────────────────────────

def _generar_cadena_silabas(longitud):
    """
    Genera una cadena de `longitud` caracteres usando sílabas
    comunes del español, para que el texto parezca natural.
    """
    resultado = []
    while len(resultado) < longitud:
        silaba = random.choice(SILABAS)
        resultado.extend(list(silaba))
    return resultado[:longitud]


def _generar_cadena_palabras(longitud):
    """
    Genera una cadena de exactamente `longitud` caracteres usando
    palabras comunes del español (sin espacios, concatenadas).
    """
    resultado = []
    while len(resultado) < longitud:
        palabra = random.choice(PALABRAS_RELLENO).upper()
        resultado.extend(list(palabra))
    return resultado[:longitud]


def generar_cobertura_automatica(posiciones_secretas, mensaje_limpio, n):
    """
    Genera un texto de cobertura de n² caracteres donde:
    - Las posiciones indicadas contienen las letras del mensaje secreto.
    - El resto está relleno con texto de aspecto español natural.

    Retorna una lista de n² caracteres.
    """
    total = n * n
    # Generar relleno con distribución de letras españolas
    relleno = list(_generar_cadena_silabas(total))

    # Insertar letras secretas en las posiciones correspondientes
    for i, pos in enumerate(posiciones_secretas):
        if i < len(mensaje_limpio):
            relleno[pos] = mensaje_limpio[i].upper()
        # Si el mensaje es más corto que los huecos, los huecos extra quedan como relleno

    return relleno


def texto_a_parrafo(chars_lista, n, palabras=True):
    """
    Convierte la lista de n² caracteres a un string de texto.
    Si palabras=True, inserta espacios cada ciertos caracteres
    para que parezca texto natural con palabras.
    """
    texto = ''.join(chars_lista)
    if not palabras:
        return texto

    # Dividir en "palabras" de longitud variable (3-6 letras)
    resultado = []
    i = 0
    random.seed(42)  # semilla fija para consistencia
    while i < len(texto):
        largo = random.randint(3, 6)
        resultado.append(texto[i:i + largo])
        i += largo
    random.seed()  # restablecer aleatoriedad

    return ' '.join(resultado)


def parrafo_a_chars(parrafo):
    """
    Extrae solo los caracteres alfabéticos de un párrafo
    (quita espacios, signos de puntuación, etc.).
    Retorna lista de caracteres en mayúsculas.
    """
    return [c.upper() for c in parrafo if c.isalpha()]


# ──────────────────────────────────────────────────────────────
# Funciones principales
# ──────────────────────────────────────────────────────────────

def ocultar_mensaje(mensaje_secreto, huecos, n, texto_manual=None):
    """
    Oculta el mensaje secreto dentro de un texto de cobertura.

    Parámetros:
        mensaje_secreto: str con el mensaje a ocultar
        huecos: set de celdas-hueco (fila, col)
        n: tamaño de la rejilla
        texto_manual: str opcional con texto de cobertura provisto por el usuario

    Retorna:
        chars_final   : list de n² caracteres (texto de cobertura con secreto incrustado)
        posiciones    : list de índices lineales donde está el secreto
        mensaje_usado : str con el mensaje que realmente se insertó (puede estar recortado)
        advertencias  : list de mensajes de advertencia
    """
    advertencias = []

    # Limpiar el mensaje secreto: solo letras mayúsculas
    mensaje_limpio = ''.join(c.upper() for c in mensaje_secreto if c.isalpha() or c == ' ')
    mensaje_sin_espacios = ''.join(c for c in mensaje_limpio if c.isalpha())

    posiciones = obtener_posiciones_lineales(huecos, n)
    capacidad = len(posiciones)

    if len(mensaje_sin_espacios) > capacidad:
        mensaje_sin_espacios = mensaje_sin_espacios[:capacidad]
        advertencias.append(
            f"El mensaje fue recortado a {capacidad} caracteres (capacidad de la rejilla)."
        )
    elif len(mensaje_sin_espacios) < capacidad:
        advertencias.append(
            f"La rejilla tiene {capacidad} huecos pero el mensaje solo tiene "
            f"{len(mensaje_sin_espacios)} caracteres. "
            f"Los huecos extra quedarán con relleno."
        )

    total = n * n

    if texto_manual:
        # Modo manual: el usuario proporciona el texto de cobertura
        chars_cobertura = parrafo_a_chars(texto_manual)
        if len(chars_cobertura) < total:
            advertencias.append(
                f"El texto de cobertura tiene solo {len(chars_cobertura)} caracteres "
                f"(se necesitan {total}). Se completará con relleno automático."
            )
            chars_cobertura += list(_generar_cadena_silabas(total - len(chars_cobertura)))
        chars_final = chars_cobertura[:total]
    else:
        # Modo automático: generar relleno
        chars_final = generar_cobertura_automatica(posiciones, mensaje_sin_espacios, n)
        return chars_final, posiciones, mensaje_sin_espacios, advertencias

    # Insertar el mensaje secreto en las posiciones de los huecos
    for i, pos in enumerate(posiciones):
        if i < len(mensaje_sin_espacios):
            chars_final[pos] = mensaje_sin_espacios[i]
        # posiciones extra: mantienen el carácter original del texto de cobertura

    return chars_final, posiciones, mensaje_sin_espacios, advertencias


def revelar_mensaje(texto_cobertura, huecos, n):
    """
    Extrae el mensaje oculto del texto de cobertura usando la rejilla.

    Parámetros:
        texto_cobertura: str con el texto (puede incluir espacios)
        huecos: set de celdas-hueco (fila, col)
        n: tamaño de la rejilla

    Retorna:
        mensaje    : str con el mensaje extraído
        posiciones : list de índices lineales donde estaba el secreto
        chars      : list de n² caracteres del texto de cobertura procesado
        error      : str o None
    """
    chars = parrafo_a_chars(texto_cobertura)
    total = n * n

    if len(chars) < total:
        return (
            "",
            [],
            chars,
            f"El texto tiene solo {len(chars)} caracteres (se necesitan {total})."
        )

    chars = chars[:total]
    posiciones = obtener_posiciones_lineales(huecos, n)
    mensaje = ''.join(chars[pos] for pos in posiciones)

    return mensaje, posiciones, chars, None


def chars_a_texto_resaltado(chars, n, posiciones_secretas):
    """
    Prepara la información para el widget Text con resaltado.
    Retorna lista de tuplas (texto_segmento, es_secreto).
    """
    pos_set = set(posiciones_secretas)
    segmentos = []
    for i, c in enumerate(chars):
        es_secreto = i in pos_set
        segmentos.append((c, es_secreto))
    return segmentos


def guardar_configuracion(huecos, n, nombre_archivo):
    """Guarda la rejilla en JSON."""
    datos = {'n': n, 'huecos': [list(h) for h in huecos]}
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2)


def cargar_configuracion(nombre_archivo):
    """Carga la rejilla desde JSON."""
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return set(tuple(h) for h in datos['huecos']), datos['n']
