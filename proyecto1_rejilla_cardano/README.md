# Proyecto 1 – Simulador de Rejilla de Cardano

## ¿Qué es la Rejilla de Cardano?

La rejilla de Cardano es una técnica de cifrado por ocultación inventada en el siglo XVI. Consiste en una plantilla cuadrada con huecos recortados que se coloca sobre un papel. Al girarla 90° en cuatro posiciones, los huecos cubren todas las celdas exactamente una vez, permitiendo ocultar un mensaje dentro de un texto que parece normal.

## Requisitos

- Python 3.10 o superior
- No requiere librerías externas (usa Tkinter, incluido en Python)

## Cómo ejecutar

```bash
cd proyecto1_rejilla_cardano
python main.py
```

## Cómo usar la aplicación

### 1. Crear una rejilla
- Elige el **tamaño** (4×4, 6×6 u 8×8) en el panel derecho.
- Haz **clic en las celdas** del canvas para marcar los huecos (en morado).
- O usa el botón **"Generar rejilla de ejemplo"** para obtener una válida automáticamente.
- La aplicación validará automáticamente que las 4 rotaciones no se superpongan.

### 2. Cifrar un mensaje
1. Escribe tu mensaje en el campo **"Mensaje"**.
2. Haz clic en **"🔒 Cifrar"**.
3. La matriz cifrada aparecerá en el campo inferior y en el canvas.
4. Usa **"▶ Paso"** o **"▶▶ Reproducir todo"** para ver la animación de cada rotación.

### 3. Descifrar un mensaje
1. Asegúrate de tener la misma rejilla con la que se cifró.
2. Pega la matriz cifrada en el campo **"Pega la matriz cifrada"** (letras separadas por espacios, una fila por línea).
3. Haz clic en **"🔓 Descifrar"**.
4. El mensaje original aparecerá en la sección **"RESULTADO"**.

### 4. Guardar y cargar rejillas
- Usa **"💾 Guardar"** para exportar tu rejilla a un archivo `.json`.
- Usa **"📂 Cargar"** para recuperar una rejilla guardada.

## Restricción matemática

Para que la rejilla sea válida, los huecos deben cumplir: al rotar la plantilla 0°, 90°, 180° y 270°, cada celda de la cuadrícula es visible exactamente **una sola vez**. Esto significa que el número de huecos debe ser exactamente `n² / 4`.

| Tamaño | Celdas totales | Huecos necesarios |
|--------|---------------|-------------------|
| 4×4    | 16            | 4                 |
| 6×6    | 36            | 9                 |
| 8×8    | 64            | 16                |
