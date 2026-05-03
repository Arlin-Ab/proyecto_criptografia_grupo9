# Documentación Técnica — Proyecto 2: Esteganografía con Rejilla de Cardano

## Objetivo

Implementar **esteganografía basada en rejilla**: ocultar un mensaje secreto dentro de un texto de cobertura aparentemente inocente, donde las posiciones marcadas por los huecos de la rejilla indican qué caracteres pertenecen al mensaje oculto.

A diferencia del cifrado (que hace el mensaje ilegible), la esteganografía **oculta la existencia misma del mensaje**.

---

## Algoritmo

### Modo Ocultar

1. Se define una rejilla n×n con huecos (n²/4 posiciones).
2. Se toma el mensaje secreto (solo letras).
3. Se genera o se proporciona un texto de cobertura de n² caracteres.
4. Las letras del mensaje se colocan en las posiciones lineales correspondientes a los huecos.
5. Las posiciones restantes se rellenan con texto de aspecto natural.
6. El resultado es un texto de cobertura que parece inocente.

### Modo Revelar

1. Se toma el texto de cobertura (ignorando espacios).
2. Se extraen los caracteres en las posiciones marcadas por los huecos de la rejilla.
3. Esos caracteres concatenados forman el mensaje secreto.

---

## Explicación matemática

Dado una rejilla de n×n con huecos H = {(f₁,c₁), (f₂,c₂), …}, cada hueco tiene una **posición lineal**:

```
pos_lineal(fila, col) = fila × n + col
```

El conjunto de posiciones lineales, ordenado de menor a mayor, determina qué índices del texto de cobertura (sin espacios) contienen el secreto.

**Ejemplo** para n=4, huecos en (0,0), (0,2), (1,1), (2,3):  
Posiciones lineales → 0, 2, 5, 11

En el texto de cobertura de 16 caracteres:
```
Índice:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
Texto:   H  o  L  a  m  A  n  d  o  x  x  Y  x  x  x  x
         ↑     ↑        ↑              ↑
       H         L         A              Y   → mensaje "HLAY"
```

---

## Ejemplo concreto

**Rejilla 4×4**, huecos en posiciones lineales [0, 5, 10, 15]  
**Mensaje secreto**: `CODA`

**Texto de cobertura generado** (modo automático):  
`CALAMANDONAPIODAO` (16 letras, sin espacios)

Con espacios para parecer natural:  
`CAL AMA NDO NAP IOD AO`

Al revelar (extraer posiciones 0, 5, 10, 15):
```
Posición 0  → C
Posición 5  → A
Posición 10 → D
Posición 15 → O
```

**Mensaje revelado**: `CADO`... (depende del relleno generado)

---

## Manual de uso

### Requisitos

- Python 3.10 o superior (Tkinter incluido)

### Ejecutar

```bash
cd proyecto2_esteganografia
python main.py
```

### Ocultar un mensaje

1. En el panel izquierdo, **configura la rejilla**: elige tamaño, marca huecos o usa "🎲 Generar rejilla válida".
2. Ve a la pestaña **"🔒 Ocultar mensaje"**.
3. Escribe el **mensaje secreto** (ej. `ATACAR AL AMANECER`).
4. Elige el modo de cobertura:
   - **Automático**: el sistema genera relleno con letras en español.
   - **Manual**: escribe tu propio texto de cobertura en el campo de texto.
5. Pulsa **"🔒 Ocultar mensaje en el texto"**.
6. El resultado aparece con las **letras secretas resaltadas en morado**.
7. Desactiva el resaltado para ver si el texto parece natural.
8. Usa **"📋 Copiar texto limpio"** para enviarlo.

### Revelar un mensaje

1. Asegúrate de tener la **misma rejilla** con la que se ocultó.
2. Ve a la pestaña **"🔓 Revelar mensaje"**.
3. Pega el texto de cobertura (con o sin espacios).
4. Pulsa **"🔓 Revelar mensaje oculto"**.
5. El mensaje secreto aparece en la sección **"MENSAJE REVELADO"**.
6. El texto de cobertura muestra las posiciones secretas resaltadas.

### Guardar / Cargar rejilla

Usa los botones **💾 Guardar** y **📂 Cargar** para guardar la configuración de la rejilla en formato JSON y reutilizarla más tarde.
