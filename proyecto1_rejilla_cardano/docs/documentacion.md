# Documentación Técnica — Proyecto 1: Rejilla de Cardano

## Objetivo

Simular el cifrado por **Rejilla de Cardano giratoria**: una plantilla cuadrada con huecos que se coloca sobre una cuadrícula y se gira 90° en cuatro posiciones, ocultando un mensaje dentro de una matriz de caracteres aparentemente aleatoria.

---

## Algoritmo

### Pasos del algoritmo de cifrado

1. Se parte de una cuadrícula de n×n celdas (n = 4, 6 u 8).
2. Se define la **rejilla**: un conjunto de n²/4 posiciones marcadas como huecos.
3. **Restricción matemática**: al rotar la rejilla 0°, 90°, 180° y 270°, cada celda de la cuadrícula debe quedar expuesta exactamente una vez.
4. El mensaje se divide en grupos de n²/4 caracteres.
5. En cada rotación (4 en total) se escriben los caracteres del mensaje en las celdas visibles, siguiendo orden de lectura (fila por fila, izquierda a derecha).
6. La cuadrícula resultante n×n contiene el mensaje oculto.

### Pasos del algoritmo de descifrado

1. Se coloca la misma rejilla en posición 0° sobre la cuadrícula cifrada.
2. Se leen los caracteres en las celdas visibles → primer grupo del mensaje.
3. Se rota la rejilla 90° y se vuelven a leer los caracteres visibles.
4. Se repite para 180° y 270°.
5. Concatenando los cuatro grupos se recupera el mensaje original.

---

## Explicación matemática

Sea una cuadrícula de n×n celdas. Una posición (fila, col) al rotarse 90° en sentido horario produce la nueva posición:

```
(fila', col') = (col, n − 1 − fila)
```

Para que la rejilla sea válida, las cuatro rotaciones de cada hueco deben caer en celdas distintas. Esto garantiza que el producto de las 4 rotaciones es una partición exacta de las n² celdas en n²/4 grupos de 4.

Número de celdas visibles por rotación: **n²/4**  
Capacidad total del mensaje: **n²** caracteres

| Tamaño | Capacidad |
|--------|-----------|
| 4×4    | 16        |
| 6×6    | 36        |
| 8×8    | 64        |

---

## Ejemplo concreto

**Rejilla 4×4** con huecos en: (0,0), (0,1), (1,1), (2,1)

**Mensaje**: `HOLAMUNDOXXXXXXX` (16 caracteres, relleno con X)

### Rotación 0°: huecos (0,0) (0,1) (1,1) (2,1) → H O L A

```
H O . .
. L . .
. A . .
. . . .
```

### Rotación 90°: huecos rotan → se escriben M U N D

```
H O . .
. L . .
. A . .
. . . .
  +
. . M .
. . . U
. . . N
. D . .
```

### Rotación 180° y 270°: se completan el resto con O X X X X X X X

**Resultado final** (cuadrícula 4×4 completa):

```
H O M X
X L X U
X A X N
X D X X
```

**Descifrado**: aplicando la rejilla en las 4 posiciones se recupera `HOLAMUNDOXXXXXXX`.

---

## Manual de uso

### Requisitos

- Python 3.10 o superior
- Sin dependencias externas (usa Tkinter)

### Ejecutar

```bash
cd proyecto1_rejilla_cardano
python main.py
```

### Pasos de uso

1. **Selecciona el tamaño** de la cuadrícula (4×4, 6×6 u 8×8) en el panel derecho.
2. **Marca los huecos** haciendo clic en las celdas del canvas. El panel muestra en verde dónde caerán las rotaciones.
3. Verifica que aparezca "✓ Rejilla válida". Si aparece un error, ajusta los huecos.
4. Puedes usar **"🎲 Generar rejilla de ejemplo"** para obtener una válida automáticamente.
5. **Para cifrar**: escribe el mensaje en el campo "Mensaje" y pulsa "🔒 Cifrar". La matriz cifrada aparece en el campo inferior.
6. **Para animar**: usa "▶ Paso" para avanzar rotación por rotación, o "▶▶ Reproducir todo" para animación automática.
7. **Para descifrar**: pega la matriz cifrada (formato: letras separadas por espacios, una fila por línea) y pulsa "🔓 Descifrar".
8. Guarda y carga rejillas con los botones **💾 / 📂**.
