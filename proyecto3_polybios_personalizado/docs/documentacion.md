# Documentación Técnica — Proyecto 3: Personalizador de Cuadrícula Polybios

## Objetivo

Implementar el **cifrado de Polybios** con una cuadrícula completamente personalizable: el usuario puede elegir el tamaño (5×5 o 6×6), la fusión de letras (I/J o N/Ñ) y reordenar las celdas mediante arrastrar y soltar.

---

## Algoritmo

### Cifrado Polybios

1. Se construye una cuadrícula n×n con símbolos únicos (letras y/o dígitos).
2. Para cifrar cada carácter del mensaje:
   a. Se busca la celda que contiene ese carácter.
   b. Se anota su posición como par (fila, columna), ambos con base 1.
   c. El par de dígitos es la representación cifrada.
3. El texto cifrado es la secuencia de pares separados por espacios.

### Descifrado Polybios

1. Se lee cada par de dígitos del texto cifrado.
2. El primer dígito es la fila (−1 para índice base 0), el segundo es la columna.
3. Se consulta la celda en esa posición y se obtiene el carácter.
4. Se concatenan todos los caracteres recuperados.

---

## Explicación matemática

La cuadrícula es una función biyectiva:

```
f: Σ → {1..n} × {1..n}
```

donde Σ es el alfabeto de símbolos. El cifrado aplica f a cada carácter:

```
cifrar(m₁m₂…mₖ) = f(m₁) f(m₂) … f(mₖ)
```

El descifrado aplica la función inversa:

```
descifrar(c₁c₂…cₖ) = f⁻¹(c₁) f⁻¹(c₂) … f⁻¹(cₖ)
```

### Fusión de celdas (IJ, NÑ)

Para acomodar el alfabeto en 25 celdas, dos letras comparten posición:
- Cifrado: ambas letras producen las mismas coordenadas.
- Descifrado: se usa la primera letra de la celda por convención.

### Cuadrículas disponibles

| Preset | n | Símbolos | Fusiones |
|--------|---|----------|---------|
| 5×5 Clásico | 5 | A-Z | I/J en misma celda |
| 5×5 Español | 5 | A-Z + Ñ (sin W) | I/J en misma celda |
| 6×6 Extendido | 6 | A-Z + Ñ + 0-9 (sin W) | Ninguna |

---

## Ejemplo concreto

**Cuadrícula 5×5 Clásico (I/J):**

```
     1    2    3    4    5
1    A    B    C    D    E
2    F    G    H   IJ    K
3    L    M    N    O    P
4    Q    R    S    T    U
5    V    W    X    Y    Z
```

**Cifrar "HOLA":**

| Letra | Búsqueda en grid | Coordenadas |
|-------|-----------------|-------------|
| H     | fila=2, col=3   | **23**      |
| O     | fila=3, col=4   | **34**      |
| L     | fila=3, col=1   | **31**      |
| A     | fila=1, col=1   | **11**      |

Resultado cifrado: `23 34 31 11`

**Descifrar `23 34 31 11`:**

| Par | fila=2,col=3 | fila=3,col=4 | fila=3,col=1 | fila=1,col=1 |
|-----|-------------|-------------|-------------|-------------|
| Letra | H | O | L | A |

Resultado: `HOLA` ✓

---

## Manual de uso

### Requisitos

- Python 3.10 o superior (Tkinter incluido)

### Ejecutar

```bash
cd proyecto3_polybios_personalizado
python main.py
```

### Personalizar la cuadrícula

1. Selecciona un **preset** en el panel izquierdo (5×5 Clásico, 5×5 Español, 6×6).
2. **Arrastra celdas** para intercambiar letras (drag & drop sobre el canvas).
3. Usa **"🎲 Aleatorizar"** para mezclar todas las celdas aleatoriamente.
4. Usa **"🔤 Estándar"** para volver al orden alfabético.
5. La aplicación valida automáticamente que no haya celdas duplicadas.
6. Guarda / carga cuadrículas personalizadas con **💾 / 📂**.

### Cifrar

1. Ve a la pestaña **"🔒 Cifrar"**.
2. Escribe el texto plano en el campo de entrada.
3. Pulsa **"🔒 Cifrar"** para ver el resultado completo con tabla de pasos.
4. Usa **"▶ Paso a paso"** para ver cada letra resaltada en la cuadrícula.
5. Usa **"▶▶ Animar todo"** para la animación automática.

### Descifrar

1. Ve a la pestaña **"🔓 Descifrar"**.
2. Ingresa las coordenadas (ej. `23 34 31 11`) en el campo.
3. Pulsa **"🔓 Descifrar"** para ver el texto recuperado con tabla de pasos.
4. La animación muestra cada par siendo localizado en la cuadrícula.
