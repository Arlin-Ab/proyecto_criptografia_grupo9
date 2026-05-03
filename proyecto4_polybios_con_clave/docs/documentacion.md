# Documentación Técnica — Proyecto 4: Cifrador Polybios con Clave

## Objetivo

Extender el cifrado Polybios del Proyecto 3 con una **palabra clave** que reorganiza el orden de las letras en la cuadrícula. Esto hace que el mismo mensaje produzca coordenadas completamente distintas según la clave utilizada, aumentando drásticamente la seguridad.

---

## Algoritmo

### Construcción de la cuadrícula con clave

1. Se toma la palabra clave (ej. `CRYPTO`).
2. Se eliminan letras duplicadas preservando el orden: `CRYPTO` → `CRYPTO` (sin duplicados).
3. Se normalizan las letras según el modo (ej. J→I en modo 5×5 IJ).
4. Estas letras únicas se colocan al inicio de la secuencia.
5. Se añaden a continuación las letras restantes del alfabeto base (en orden), excluyendo las ya usadas en la clave.
6. La secuencia resultante se coloca en la cuadrícula fila por fila.

### Cifrado y descifrado

Idéntico al Proyecto 3 pero usando la cuadrícula generada por la clave.

---

## Explicación matemática

Sea `K` la palabra clave sin duplicados y `Σ` el alfabeto base del modo:

```
secuencia = [letras de K] + [c ∈ Σ | c ∉ K]
```

Esta secuencia tiene exactamente n² elementos (25 para 5×5, 36 para 6×6).

La cuadrícula resultante es:

```
grid[i][j] = secuencia[i × n + j]
```

### Ejemplo con clave "CRYPTO" en 5×5 IJ

```
Clave sin duplicados: C R Y P T O
Resto del alfabeto:  A B D E F G H I K L M N Q S U V W X Z
Secuencia completa:  C R Y P T O A B D E F G H I K L M N Q S U V W X Z
```

Cuadrícula resultante:
```
     1    2    3    4    5
1    C    R    Y    P    T
2    O    A    B    D    E
3    F    G    H   IJ    K
4    L    M    N    Q    S
5    U    V    W    X    Z
```

Con esta cuadrícula, `HOLA` se cifra como: `35 22 43 22`  
Con la cuadrícula estándar, `HOLA` se cifraría como: `23 34 31 11`

### Análisis de seguridad

| Cuadrícula | Celdas | Permutaciones | Bits de entropía |
|------------|--------|---------------|-----------------|
| 5×5        | 25     | 25! ≈ 1.55×10²⁵ | ~83 bits      |
| 6×6        | 36     | 36! ≈ 3.72×10⁴¹ | ~138 bits     |

> ⚠ Polybios es un cifrado de sustitución monoalfabética susceptible a análisis de frecuencias. Su valor es didáctico, no criptográfico moderno.

---

## Ejemplo concreto

**Clave**: `PYTHON`  
**Modo**: 5×5 IJ  
**Texto**: `SECRETO`

1. Normalizar clave: `P Y T H O N` (sin duplicados, J→I ya no aplica)
2. Resto: `A B C D E F G I K L M Q R S U V W X Z`
3. Cuadrícula generada:
```
     1    2    3    4    5
1    P    Y    T    H    O
2    N    A    B    C    D
3    E    F    G   IJ    K
4    L    M    Q    R    S
5    U    V    W    X    Z
```
4. Cifrar `SECRETO`:
   - S → (4,5) → `45`
   - E → (3,1) → `31`
   - C → (2,4) → `24`
   - R → (4,4) → `44`
   - E → `31`
   - T → (1,3) → `13`
   - O → (1,5) → `15`
5. Resultado: `45 31 24 44 31 13 15`

---

## Manual de uso

### Requisitos

- Python 3.10 o superior (Tkinter incluido)

### Ejecutar

```bash
cd proyecto4_polybios_con_clave
python main.py
```

### Generar la cuadrícula con clave

1. Selecciona el **modo** en el panel izquierdo (5×5 IJ, 5×5 NÑ, 6×6).
2. Escribe la **palabra clave** en el campo de texto (ej. `CRYPTO`).
3. Pulsa **⚙ Generar** o Enter.
4. La cuadrícula aparece en el canvas central con las letras de la clave resaltadas en morado y el relleno en azul.
5. Usa **"▶ Paso"** para ver la construcción animada celda por celda.

### Cifrar y descifrar

- Escribe el texto en el campo **"Texto plano"** del panel izquierdo.
- Usa **"🔒 Cifrar"** o **"🔓 Descifrar"** según el caso.
- Usa **"▶ Paso"** para ver cada letra resaltada en la cuadrícula.
- La tabla de pasos muestra: letra → fila → columna → coordenadas.

### Modo comparación (pestaña ⚖)

- Muestra la cuadrícula estándar y la cuadrícula con clave lado a lado.
- Las celdas en rojo indican posiciones que cambian respecto al estándar.
- Cifra el mismo texto con ambas cuadrículas para ver la diferencia.

### Análisis de seguridad (pestaña 🔐)

- Muestra el número total de permutaciones posibles.
- Indica la entropía en bits y la compara con estándares (DES, AES-128, etc.).

### Guardar / cargar configuración

Usa **💾 Guardar** y **📂 Cargar** para persistir la cuadrícula y la clave en formato JSON.
