# Proyecto 3 – Personalizador de Cuadrícula Polybios

## ¿Qué es el cifrado Polybios?

El cifrado Polybios (siglo II a.C.) convierte cada letra en un par de coordenadas `(fila, columna)` dentro de una cuadrícula cuadrada. Por ejemplo, con la cuadrícula estándar: `HOLA` → `23 35 31 11`.

## Requisitos

- Python 3.10 o superior
- Solo usa Tkinter (incluido en Python estándar)

## Cómo ejecutar

```bash
cd proyecto3_polybios_personalizado
python main.py
```

## Presets disponibles

| Preset | Tamaño | Descripción |
|--------|--------|-------------|
| 5×5 Clásico (I/J) | 5×5 | A–Z con I y J en la misma celda, sin Ñ |
| 5×5 Español | 5×5 | A–Z con I/J fusionados, incluye Ñ, sin W |
| 6×6 Extendido | 6×6 | Letras A–Z + Ñ (sin W) + dígitos 0–9 |

## Cómo usar la aplicación

### 1. Personalizar la cuadrícula

- Selecciona un **preset** en el panel izquierdo.
- **Arrastra y suelta** las celdas para cambiar su posición.
- Usa **"🎲 Aleatorizar"** para mezclar aleatoriamente.
- Usa **"🔤 Estándar"** para volver al preset original.
- Guarda / carga tu cuadrícula personalizada con los botones **💾 / 📂**.

### 2. Cifrar un texto

1. Escribe el texto en el campo **"TEXTO PLANO"** (pestaña 🔒 Cifrar).
2. Pulsa **"🔒 Cifrar"** para ver el resultado completo.
3. Usa **"▶ Paso a paso"** para avanzar letra por letra (se resalta la celda correspondiente en la cuadrícula).
4. Usa **"▶▶ Animar todo"** para la animación automática.

### 3. Descifrar coordenadas

1. Escribe las coordenadas en el campo **"COORDENADAS CIFRADAS"** (pestaña 🔓 Descifrar).
   - Formato: `23 35 31 11` (pares separados por espacios)
2. Pulsa **"🔓 Descifrar"** para ver el resultado.
3. La animación muestra cada par siendo buscado en la cuadrícula.

## Celdas fusionadas

Las celdas que muestran dos caracteres (como `IJ` o `NÑ`) indican que ambas letras se cifran con las mismas coordenadas. Al descifrar, se usa la primera letra de la celda.

## Ejemplo

Con el preset **5×5 Clásico (I/J)**:

```
    1  2  3  4  5
1   A  B  C  D  E
2   F  G  H  IJ K
3   L  M  N  O  P
4   Q  R  S  T  U
5   V  W  X  Y  Z
```

`HOLA` → `H(2,3)` `O(3,4)` `L(3,1)` `A(1,1)` → **`23 34 31 11`**
