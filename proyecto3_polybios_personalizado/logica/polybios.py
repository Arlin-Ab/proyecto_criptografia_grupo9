# polybios.py - Lógica del Proyecto 3: Cuadrícula Polybios Personalizable
#
# El cifrado Polybios codifica cada letra como un par de coordenadas (fila, columna)
# en una cuadrícula cuadrada. Cada celda puede contener uno o dos caracteres
# fusionados (ej. "IJ" o "NÑ").

import json
import random
import copy

# ──────────────────────────────────────────────────────────────
# Cuadrículas predefinidas
# ──────────────────────────────────────────────────────────────

# 5×5 clásico: fusiona I y J, sin Ñ
PRESET_5x5_IJ = [
    ['A',  'B',  'C',  'D',  'E'],
    ['F',  'G',  'H',  'IJ', 'K'],
    ['L',  'M',  'N',  'O',  'P'],
    ['Q',  'R',  'S',  'T',  'U'],
    ['V',  'W',  'X',  'Y',  'Z'],
]

# 5×5 español: fusiona I/J, incluye Ñ, sin W
PRESET_5x5_NÑ = [
    ['A',  'B',  'C',  'D',  'E'],
    ['F',  'G',  'H',  'IJ', 'K'],
    ['L',  'M',  'N',  'Ñ',  'O'],
    ['P',  'Q',  'R',  'S',  'T'],
    ['U',  'V',  'X',  'Y',  'Z'],
]

# 6×6: letras A-Z + Ñ (sin W) + dígitos 0-9 = 36 símbolos
PRESET_6x6 = [
    ['A',  'B',  'C',  'D',  'E',  'F'],
    ['G',  'H',  'I',  'J',  'K',  'L'],
    ['M',  'N',  'Ñ',  'O',  'P',  'Q'],
    ['R',  'S',  'T',  'U',  'V',  'X'],
    ['Y',  'Z',  '0',  '1',  '2',  '3'],
    ['4',  '5',  '6',  '7',  '8',  '9'],
]

PRESETS = {
    '5x5_IJ':  {'grid': PRESET_5x5_IJ,  'nombre': '5×5 Clásico (I/J fusionados)'},
    '5x5_NÑ':  {'grid': PRESET_5x5_NÑ,  'nombre': '5×5 Español (I/J, incluye Ñ, sin W)'},
    '6x6':     {'grid': PRESET_6x6,      'nombre': '6×6 Extendido (letras + dígitos 0-9)'},
}


# ──────────────────────────────────────────────────────────────
# Funciones auxiliares
# ──────────────────────────────────────────────────────────────

def clonar_grid(grid):
    """Devuelve una copia profunda de la cuadrícula."""
    return copy.deepcopy(grid)


def construir_mapa(grid):
    """
    Construye un diccionario {carácter: (fila, col)} para búsqueda rápida.
    Celdas fusionadas (ej. "IJ") mapean CADA uno de sus caracteres al mismo par.
    """
    mapa = {}
    for i, fila in enumerate(grid):
        for j, celda in enumerate(fila):
            for letra in celda.upper():
                mapa[letra] = (i, j)
    return mapa


def validar_grid(grid):
    """
    Valida que la cuadrícula sea correcta:
    - Ninguna celda vacía.
    - No hay caracteres repetidos entre celdas distintas.
    Retorna (True, "") o (False, mensaje_de_error).
    """
    vistos = {}
    for i, fila in enumerate(grid):
        for j, celda in enumerate(fila):
            if not celda:
                return False, f"La celda ({i+1},{j+1}) está vacía."
            for letra in celda.upper():
                if letra in vistos:
                    fi, fj = vistos[letra]
                    return False, (
                        f"El carácter '{letra}' aparece en ({fi+1},{fj+1}) "
                        f"y también en ({i+1},{j+1})."
                    )
                vistos[letra] = (i, j)
    return True, ""


def aleatorizar_grid(grid):
    """Mezcla aleatoriamente las celdas de la cuadrícula."""
    n = len(grid)
    celdas = [grid[i][j] for i in range(n) for j in range(n)]
    random.shuffle(celdas)
    nueva = []
    for i in range(n):
        fila = celdas[i * n:(i + 1) * n]
        nueva.append(fila)
    return nueva


# ──────────────────────────────────────────────────────────────
# Cifrado y descifrado
# ──────────────────────────────────────────────────────────────

def cifrar(texto, grid):
    """
    Cifra el texto usando la cuadrícula Polybios.

    Retorna:
        cifrado : str con pares de coordenadas separados por espacios (ej. "23 35 31 11")
        pasos   : lista de dicts con info de cada letra procesada
        omitidos: lista de caracteres que no pudieron cifrarse
    """
    mapa = construir_mapa(grid)
    pares = []
    pasos = []
    omitidos = []

    for char in texto.upper():
        if char == ' ':
            # Los espacios se representan como separadores visuales
            if pasos:
                pasos[-1]['es_fin_palabra'] = True
            continue

        if char in mapa:
            fila, col = mapa[char]
            coord = f"{fila + 1}{col + 1}"
            pares.append(coord)
            pasos.append({
                'letra':        char,
                'fila':         fila,
                'col':          col,
                'coord':        coord,
                'celda':        grid[fila][col],
                'es_fin_palabra': False,
            })
        else:
            omitidos.append(char)

    return ' '.join(pares), pasos, omitidos


def descifrar(texto_cifrado, grid):
    """
    Descifra una secuencia de coordenadas Polybios.
    Acepta formatos: "11 23 45", "112345", "11,23,45".

    Retorna:
        descifrado : str con el texto recuperado
        pasos      : lista de dicts con info de cada par procesado
        errores    : lista de tokens que no pudieron descifrarse
    """
    n = len(grid)
    # Normalizar separadores
    limpio = texto_cifrado.replace(',', ' ').replace('-', ' ').strip()
    tokens = limpio.split()

    resultado = []
    pasos = []
    errores = []

    for token in tokens:
        token = token.strip()
        if len(token) != 2:
            if token:
                errores.append(token)
            continue
        try:
            fila = int(token[0]) - 1
            col  = int(token[1]) - 1
            if 0 <= fila < n and 0 <= col < n:
                celda = grid[fila][col]
                # En celdas fusionadas (IJ), devolvemos el primero por convención
                letra = celda[0]
                resultado.append(letra)
                pasos.append({
                    'coord': token,
                    'fila':  fila,
                    'col':   col,
                    'celda': celda,
                    'letra': letra,
                })
            else:
                errores.append(token)
        except (ValueError, IndexError):
            errores.append(token)

    return ''.join(resultado), pasos, errores


# ──────────────────────────────────────────────────────────────
# Persistencia
# ──────────────────────────────────────────────────────────────

def guardar_grid(grid, nombre_archivo):
    """Guarda la cuadrícula en un archivo JSON."""
    datos = {
        'n': len(grid),
        'grid': grid,
    }
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def cargar_grid(nombre_archivo):
    """Carga la cuadrícula desde un archivo JSON."""
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return datos['grid'], datos['n']


# ──────────────────────────────────────────────────────────────
# Utilidades de presentación
# ──────────────────────────────────────────────────────────────

def grid_a_texto(grid):
    """Convierte la cuadrícula a una representación de texto para mostrar."""
    n = len(grid)
    encabezado = "    " + "  ".join(str(j + 1) for j in range(n))
    filas = [encabezado]
    for i, fila in enumerate(grid):
        celdas = "  ".join(c.center(3) for c in fila)
        filas.append(f"{i + 1}   {celdas}")
    return '\n'.join(filas)
