# Proyecto 2 – Esteganografía con Rejilla de Cardano

## ¿Qué es la esteganografía?

A diferencia del cifrado (que hace el mensaje ilegible), la esteganografía **oculta la existencia misma del mensaje** dentro de un texto aparentemente inocente. Quien no sabe que hay un mensaje oculto, simplemente lee el texto de cobertura sin sospechar nada.

En este proyecto, la rejilla de Cardano determina qué posiciones del texto contienen el mensaje secreto. Las demás posiciones forman el texto de cobertura.

## Requisitos

- Python 3.10 o superior
- Solo usa Tkinter (incluido en Python estándar)

## Cómo ejecutar

```bash
cd proyecto2_esteganografia
python main.py
```

## Cómo usar la aplicación

### 1. Configurar la rejilla

- Elige el **tamaño** (4×4 = 4 caracteres, 6×6 = 9, 8×8 = 16).
- Haz **clic en las celdas** del canvas para marcar huecos (en morado).
- O usa **"Generar rejilla válida"** para obtener una automáticamente.
- Los números dentro de las celdas indican su **posición lineal** (0-indexed) en el texto.

### 2. Ocultar un mensaje (pestaña 🔒)

1. Escribe el **mensaje secreto** (ej. `ATACAR`).
2. Elige el modo de cobertura:
   - **Automático:** el sistema genera texto de relleno en español.
   - **Manual:** tú escribes el texto de cobertura (debe tener suficientes letras).
3. Pulsa **"🔒 Ocultar mensaje en el texto"**.
4. El resultado muestra el texto de cobertura con las **letras secretas resaltadas** en morado.
5. Activa/desactiva el resaltado para ver si el texto parece natural.
6. Usa **"📋 Copiar texto limpio"** para copiar el texto sin resaltado.

### 3. Revelar un mensaje (pestaña 🔓)

1. Asegúrate de tener la misma rejilla con la que se ocultó el mensaje.
2. Pega el texto de cobertura en el campo.
3. Pulsa **"🔓 Revelar mensaje oculto"**.
4. El mensaje secreto aparece en la sección **"MENSAJE REVELADO"**.
5. El texto de cobertura se muestra con las posiciones secretas resaltadas.

## Ejemplo rápido

Con rejilla 4×4 (huecos en posiciones 0, 5, 10, 15):

| Posición | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|----------|---|---|---|---|---|---|---|---|---|---|----|----|----|----|----|-----|
| Texto    | **H** | O | L | A | M | **O** | L | A | M | U | **N** | D | O | X | X | **D** |
| Tipo     | secreto | relleno | relleno | relleno | relleno | secreto | ... | | | | secreto | | | | | secreto |

Mensaje oculto: **HOND**

## Principio matemático

El número de huecos de la rejilla determina cuántos caracteres secretos caben:

| Tamaño | Huecos | Caracteres secretos |
|--------|--------|---------------------|
| 4×4    | 4      | 4                   |
| 6×6    | 9      | 9                   |
| 8×8    | 16     | 16                  |
