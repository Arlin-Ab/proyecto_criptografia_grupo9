# rejilla.py - Lógica de la Rejilla de Cardano
# Implementa la creación, validación, rotación y cifrado/descifrado

import json


def rotar_rejilla_90(rejilla, n):
    """
    Rota la rejilla 90 grados en sentido horario.
    Para una celda (fila, col) en una cuadrícula n×n,
    la nueva posición es (col, n-1-fila).
    """
    nueva = set()
    for (fila, col) in rejilla:
        nueva.add((col, n - 1 - fila))
    return nueva


def obtener_todas_rotaciones(rejilla, n):
    """
    Devuelve lista de 4 conjuntos de huecos:
    [0°, 90°, 180°, 270°]
    """
    rotaciones = [rejilla]
    actual = rejilla
    for _ in range(3):
        actual = rotar_rejilla_90(actual, n)
        rotaciones.append(actual)
    return rotaciones


def validar_rejilla(huecos, n):
    """
    Valida que la rejilla sea correcta:
    - Las 4 rotaciones deben cubrir exactamente cada celda UNA sola vez.
    Retorna (True, "") si es válida, o (False, mensaje_error) si no.
    """
    if not huecos:
        return False, "La rejilla no tiene huecos marcados."

    # Total de celdas debe ser divisible entre 4
    total_celdas = n * n
    if total_celdas % 4 != 0:
        return False, f"La cuadrícula {n}×{n} no es divisible entre 4."

    huecos_esperados = total_celdas // 4
    if len(huecos) != huecos_esperados:
        return False, (
            f"Se esperan {huecos_esperados} huecos para una cuadrícula {n}×{n}, "
            f"pero hay {len(huecos)}."
        )

    rotaciones = obtener_todas_rotaciones(huecos, n)

    # Verificar que todas las rotaciones sean disjuntas
    todas = []
    for r in rotaciones:
        todas.extend(r)

    if len(todas) != len(set(todas)):
        return False, "Las rotaciones de la rejilla se superponen. Elige otros huecos."

    if len(set(todas)) != total_celdas:
        return False, "Las rotaciones no cubren todas las celdas de la cuadrícula."

    return True, ""


def cifrar(mensaje, huecos, n):
    """
    Cifra el mensaje usando la rejilla de Cardano.
    Retorna la matriz n×n con el texto cifrado y
    la lista de pasos [(rotacion_idx, huecos_activos, letras_colocadas)].
    """
    # Preparar mensaje: solo letras mayúsculas, relleno con X si es necesario
    texto = mensaje.upper().replace(" ", "")
    texto = ''.join(c for c in texto if c.isalpha())

    rotaciones = obtener_todas_rotaciones(huecos, n)
    total_huecos = n * n  # todas las celdas se cubren en 4 rotaciones
    capacidad = len(huecos) * 4  # caracteres que caben en la rejilla

    # Recortar o rellenar el mensaje
    if len(texto) < capacidad:
        texto = texto + 'X' * (capacidad - len(texto))
    else:
        texto = texto[:capacidad]

    # Matriz resultado (inicialmente vacía)
    matriz = [['' for _ in range(n)] for _ in range(n)]

    pasos = []
    idx_char = 0

    for rot_idx, rot_huecos in enumerate(rotaciones):
        # Ordenar los huecos de izquierda a derecha, de arriba abajo
        huecos_ordenados = sorted(rot_huecos, key=lambda c: (c[0], c[1]))
        letras_paso = {}

        for (fila, col) in huecos_ordenados:
            if idx_char < len(texto):
                matriz[fila][col] = texto[idx_char]
                letras_paso[(fila, col)] = texto[idx_char]
                idx_char += 1

        pasos.append({
            'rotacion': rot_idx * 90,
            'huecos': list(rot_huecos),
            'letras': letras_paso
        })

    return matriz, pasos, texto


def descifrar(matriz, huecos, n):
    """
    Descifra la matriz usando la rejilla de Cardano.
    Retorna el mensaje descifrado y la lista de pasos.
    """
    rotaciones = obtener_todas_rotaciones(huecos, n)
    mensaje = []
    pasos = []

    for rot_idx, rot_huecos in enumerate(rotaciones):
        huecos_ordenados = sorted(rot_huecos, key=lambda c: (c[0], c[1]))
        letras_paso = {}

        for (fila, col) in huecos_ordenados:
            letra = matriz[fila][col] if matriz[fila][col] else '?'
            mensaje.append(letra)
            letras_paso[(fila, col)] = letra

        pasos.append({
            'rotacion': rot_idx * 90,
            'huecos': list(rot_huecos),
            'letras': letras_paso
        })

    return ''.join(mensaje), pasos


def guardar_rejilla(huecos, n, nombre_archivo):
    """Guarda la configuración de la rejilla en un archivo JSON."""
    datos = {
        'n': n,
        'huecos': [list(h) for h in huecos]
    }
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2)


def cargar_rejilla(nombre_archivo):
    """Carga la configuración de la rejilla desde un archivo JSON."""
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    n = datos['n']
    huecos = set(tuple(h) for h in datos['huecos'])
    return huecos, n


def generar_rejilla_ejemplo(n):
    """
    Genera una rejilla válida de ejemplo para tamaño n×n.
    Usa un algoritmo que garantiza que las 4 rotaciones sean disjuntas.
    """
    huecos = set()
    visitadas = set()

    for fila in range(n):
        for col in range(n):
            if (fila, col) not in visitadas:
                # Calcular las 4 rotaciones de esta celda
                celda = (fila, col)
                grupo = [celda]
                actual = celda
                for _ in range(3):
                    actual = (actual[1], n - 1 - actual[0])
                    grupo.append(actual)

                # Si todas las rotaciones son distintas y no visitadas, usar esta celda
                grupo_set = set(grupo)
                if len(grupo_set) == 4 and not grupo_set.intersection(visitadas):
                    huecos.add(celda)
                    visitadas.update(grupo_set)

    return huecos


def matriz_a_texto(matriz):
    """Convierte la matriz n×n a string para mostrar."""
    return '\n'.join(' '.join(fila) for fila in matriz)
