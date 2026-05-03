# polybios_clave.py - Lógica del Proyecto 4: Polybios con Clave
#
# Extiende el cifrado Polybios del Proyecto 3 añadiendo una palabra clave
# que reordena las letras de la cuadrícula, aumentando la seguridad.
#
# Algoritmo de construcción con clave:
#   1. Tomar la clave y eliminar letras repetidas
#   2. Colocar esas letras al inicio de la cuadrícula
#   3. Continuar con las letras del alfabeto base que NO están en la clave

import json
import math
import copy

# ──────────────────────────────────────────────────────────────
# Modos de cuadrícula disponibles
# ──────────────────────────────────────────────────────────────

MODOS = {
    '5x5_IJ': {
        'n': 5,
        # Símbolos base en orden estándar (sin J, que se fusiona con I)
        'simbolos': list('ABCDEFGHIKLMNOPQRSTUVWXYZ'),  # 25
        # Mapeo para normalizar entrada: J → I (comparten celda)
        'fusion_entrada': {'J': 'I'},
        # Cómo mostrar la celda fusionada en pantalla
        'celda_display': {'I': 'IJ'},
        'nombre': '5×5 (I/J fusionados, sin Ñ)',
    },
    '5x5_NÑ': {
        'n': 5,
        # Sin J (→I), sin W, con Ñ
        'simbolos': list('ABCDEFGHIKLMNÑOPQRSTUVXYZ'),  # 25
        'fusion_entrada': {'J': 'I'},
        'celda_display': {'I': 'IJ'},
        'nombre': '5×5 (I/J fusionados, con Ñ, sin W)',
    },
    '6x6': {
        'n': 6,
        # Sin W, con Ñ, más dígitos 0-9
        'simbolos': list('ABCDEFGHIJKLMNÑOPQRSTUVXYZ0123456789'),  # 36
        'fusion_entrada': {},
        'celda_display': {},
        'nombre': '6×6 (letras + dígitos 0-9)',
    },
}


# ──────────────────────────────────────────────────────────────
# Construcción de la cuadrícula con clave
# ──────────────────────────────────────────────────────────────

def eliminar_duplicados(texto):
    """Elimina caracteres duplicados preservando el orden de aparición."""
    vistos = set()
    resultado = []
    for c in texto:
        if c not in vistos:
            vistos.add(c)
            resultado.append(c)
    return resultado


def normalizar_clave(clave, modo_key):
    """
    Normaliza los caracteres de la clave según el modo:
    - Convierte a mayúsculas
    - Aplica fusiones (J→I si modo IJ/NÑ)
    - Descarta caracteres que no pertenecen al alfabeto del modo
    """
    modo   = MODOS[modo_key]
    fusion = modo['fusion_entrada']
    base   = set(modo['simbolos'])
    result = []
    for c in clave.upper():
        c = fusion.get(c, c)   # aplicar fusión (ej. J→I)
        if c is not None and c in base:
            result.append(c)
    return result


def construir_secuencia(clave, modo_key):
    """
    Construye la secuencia completa de símbolos para llenar la cuadrícula:
        [letras de la clave sin repetir] + [resto del alfabeto base en orden]

    Retorna la lista de símbolos y los pasos de construcción.
    """
    modo    = MODOS[modo_key]
    simbolos_base = modo['simbolos']

    # Normalizar y deduplicar la clave
    clave_norm   = normalizar_clave(clave, modo_key)
    clave_unica  = eliminar_duplicados(clave_norm)

    # Letras del alfabeto base que no están en la clave
    clave_set    = set(clave_unica)
    restante     = [s for s in simbolos_base if s not in clave_set]

    secuencia    = clave_unica + restante

    # Generar pasos para la animación
    pasos = []
    for i, simbolo in enumerate(secuencia):
        pasos.append({
            'posicion': i,
            'simbolo':  simbolo,
            'origen':   'clave' if simbolo in clave_set else 'relleno',
        })

    return secuencia, pasos


def secuencia_a_grid(secuencia, n):
    """Convierte una secuencia de n² símbolos en una cuadrícula n×n."""
    grid = []
    for i in range(n):
        fila = secuencia[i * n:(i + 1) * n]
        grid.append(fila)
    return grid


def construir_grid_con_clave(clave, modo_key):
    """
    Construye la cuadrícula Polybios a partir de la clave.

    Retorna:
        grid   : lista 2D de símbolos
        pasos  : pasos de construcción para la animación
        error  : str o None
    """
    modo = MODOS[modo_key]
    n    = modo['n']

    if not clave.strip():
        return None, [], "La clave no puede estar vacía."

    # Verificar que la clave tenga al menos un símbolo válido
    clave_norm = normalizar_clave(clave, modo_key)
    if not clave_norm:
        return None, [], (
            "La clave no contiene ninguna letra válida para este modo. "
            "Prueba con otra clave."
        )

    secuencia, pasos = construir_secuencia(clave, modo_key)

    if len(secuencia) != n * n:
        return None, [], (
            f"Error interno: se generaron {len(secuencia)} símbolos "
            f"pero se esperaban {n * n}."
        )

    grid = secuencia_a_grid(secuencia, n)
    return grid, pasos, None


def grid_estandar(modo_key):
    """
    Devuelve la cuadrícula estándar (orden alfabético) para el modo dado.
    Equivale a llamar construir_grid_con_clave con clave vacía.
    """
    modo     = MODOS[modo_key]
    n        = modo['n']
    secuencia = modo['simbolos']
    return secuencia_a_grid(secuencia, n)


# ──────────────────────────────────────────────────────────────
# Cifrado y descifrado (igual que Proyecto 3)
# ──────────────────────────────────────────────────────────────

def construir_mapa(grid, modo_key):
    """
    Construye el diccionario {carácter → (fila, col)}.
    Aplica la fusión de entrada definida en el modo.
    """
    modo   = MODOS[modo_key]
    fusion = modo['fusion_entrada']
    mapa   = {}
    for i, fila in enumerate(grid):
        for j, celda in enumerate(fila):
            mapa[celda.upper()] = (i, j)
    # Registrar también las letras fusionadas
    for src, dst in fusion.items():
        if dst and dst in mapa:
            mapa[src.upper()] = mapa[dst.upper()]
    return mapa


def cifrar(texto, grid, modo_key):
    """
    Cifra el texto con la cuadrícula.
    Retorna (cifrado_str, pasos, omitidos).
    """
    mapa    = construir_mapa(grid, modo_key)
    fusion  = MODOS[modo_key]['fusion_entrada']
    pares   = []
    pasos   = []
    omitidos = []

    for char in texto.upper():
        if char == ' ':
            if pasos:
                pasos[-1]['es_fin_palabra'] = True
            continue
        c = fusion.get(char, char)
        if c is not None and c in mapa:
            fila, col = mapa[c]
            coord = f"{fila + 1}{col + 1}"
            pares.append(coord)
            pasos.append({
                'letra':         char,
                'fila':          fila,
                'col':           col,
                'coord':         coord,
                'celda':         grid[fila][col],
                'es_fin_palabra': False,
            })
        else:
            omitidos.append(char)

    return ' '.join(pares), pasos, omitidos


def descifrar(texto_cifrado, grid):
    """
    Descifra una secuencia de coordenadas.
    Retorna (descifrado_str, pasos, errores).
    """
    n      = len(grid)
    limpio = texto_cifrado.replace(',', ' ').replace('-', ' ').strip()
    tokens = limpio.split()
    resultado = []
    pasos     = []
    errores   = []

    for token in tokens:
        if len(token) != 2:
            if token:
                errores.append(token)
            continue
        try:
            fila = int(token[0]) - 1
            col  = int(token[1]) - 1
            if 0 <= fila < n and 0 <= col < n:
                celda = grid[fila][col]
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
# Análisis de seguridad
# ──────────────────────────────────────────────────────────────

def analisis_seguridad(modo_key):
    """
    Calcula estadísticas de seguridad para el modo dado.

    Retorna un dict con:
        - total_permutaciones : n²! posibles cuadrículas
        - bits_entropia       : log2(n²!) bits de entropía
        - descripcion         : texto explicativo
    """
    modo = MODOS[modo_key]
    n    = modo['n']
    total_celdas = n * n

    total_perms = math.factorial(total_celdas)
    bits        = math.log2(total_perms)

    return {
        'n':                  n,
        'total_celdas':       total_celdas,
        'total_permutaciones': total_perms,
        'bits_entropia':      bits,
        'notacion_cientifica': f"{total_perms:.3e}",
    }


def comparar_grids(grid_std, grid_clave, modo_key):
    """
    Compara celda a celda la cuadrícula estándar y la generada con clave.
    Retorna una máscara booleana: True donde son iguales, False donde difieren.
    """
    n = len(grid_std)
    mascara = []
    for i in range(n):
        fila = []
        for j in range(n):
            igual = grid_std[i][j] == grid_clave[i][j]
            fila.append(igual)
        mascara.append(fila)
    return mascara


# ──────────────────────────────────────────────────────────────
# Persistencia
# ──────────────────────────────────────────────────────────────

def guardar_configuracion(grid, clave, modo_key, nombre_archivo):
    """Guarda la cuadrícula y la clave en un archivo JSON."""
    datos = {
        'modo':  modo_key,
        'clave': clave,
        'n':     len(grid),
        'grid':  grid,
    }
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def cargar_configuracion(nombre_archivo):
    """Carga la cuadrícula y la clave desde un archivo JSON."""
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return datos['grid'], datos.get('clave', ''), datos.get('modo', '5x5_IJ')
