# Documentación Técnica — Proyecto 5: Criptógrafo de Wheatstone

## Objetivo

Simular el **mecanismo físico del criptógrafo de Wheatstone** (1867): dos discos concéntricos con 27 y 26 posiciones respectivamente, conectados por engranajes que se desfasan en cada paso. Este desfase garantiza que letras repetidas en el texto claro produzcan letras cifradas distintas.

---

## Algoritmo

### Cifrado de Wheatstone

1. Inicializar ambas agujas en posición 0 (letra A en el disco exterior, letra A en el interior).
2. Para cada carácter del texto (espacios → `_`):
   a. Localizar el carácter en el **disco exterior** (27 posiciones).
   b. Calcular el **avance** necesario para llegar a él, siempre en sentido horario (nunca se retrocede). Si ya apuntamos a esa posición, se da una vuelta completa (27 pasos).
   c. Avanzar **ambas agujas** ese mismo número de pasos.
   d. La letra señalada por la aguja del **disco interior** es el carácter cifrado.
3. El texto cifrado es la concatenación de todas las letras del disco interior.

### Descifrado de Wheatstone

1. Inicializar ambas agujas en posición 0.
2. Para cada carácter del texto cifrado:
   a. Localizar el carácter en el **disco interior** (26 posiciones).
   b. Calcular el avance necesario, siempre hacia adelante.
   c. Avanzar ambas agujas ese número de pasos.
   d. La letra señalada por la aguja del **disco exterior** es el carácter original.

---

## Explicación matemática

Sean:
- `E = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"` (disco exterior, 27 posiciones)
- `I = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"` (disco interior, 26 posiciones)
- `p_e`, `p_i` posiciones actuales de las agujas (enteros)

**Avance para cifrar un carácter c:**

```
idx  = E.index(c)
paso = (idx − p_e) mod 27
si paso == 0: paso = 27      ← nunca detenerse en el mismo lugar
```

**Actualización de posiciones:**

```
p_e = (p_e + paso) mod 27
p_i = (p_i + paso) mod 26
```

**Letra cifrada:**

```
letra_cifrada = I[p_i]
```

### Por qué letras repetidas se cifran distinto

Como el disco exterior tiene 27 posiciones y el interior 26, cada avance **desincroniza** el estado relativo de los dos discos en 1 posición (mod 1):

```
desfase = (p_e − p_i) mod 26
```

Este desfase cambia con cada letra procesada. Por lo tanto, aunque se cifren dos `A` seguidas, las posiciones de los discos son distintas en cada caso, produciendo letras cifradas diferentes.

### Efecto del espacio en blanco

El carácter espacio se convierte en `_` (posición 26 del disco exterior). Al procesarlo, el avance hasta `_` es generalmente mayor que para letras normales, produciendo un desfase adicional que "desincroniza" el contexto para la siguiente palabra.

---

## Ejemplo concreto

**Cifrar "AAAA"** (posiciones iniciales ambas en 0 = letra A):

| Paso | Letra | Avance | p_e (antes→después) | p_i (antes→después) | Cifrada |
|------|-------|--------|---------------------|---------------------|---------|
| 1 | A | 27 (vuelta completa) | 0→0 | 0→1 | B |
| 2 | A | 27 | 0→0 | 1→2 | C |
| 3 | A | 27 | 0→0 | 2→3 | D |
| 4 | A | 27 | 0→0 | 3→4 | E |

**Resultado**: `BCDE` — cada `A` se cifra distinto.

**Cifrar "HOLA MUNDO"** → incluye un espacio que rompe el contexto entre las dos palabras.

---

## Manual de uso

### Requisitos

- Python 3.10 o superior (Tkinter incluido)

### Ejecutar

```bash
cd proyecto5_wheatstone
python main.py
```

### Panel izquierdo — Discos de Wheatstone

- **Disco exterior** (azul, 27 posiciones): A–Z más el símbolo `_` para el espacio.
- **Disco interior** (amarillo, 26 posiciones): A–Z.
- Las agujas se mueven suavemente a cada nuevo paso.
- El canvas se redimensiona automáticamente con la ventana.

### Panel derecho — Controles

1. **Escribe el texto** en el campo de entrada.
2. Pulsa **"🔒 Iniciar Cifrado"** o **"🔓 Iniciar Descifrado"**.
3. La animación avanza automáticamente paso a paso.
4. Usa **"▶ Paso a Paso"** para avanzar manualmente un carácter.
5. Usa **"▶▶ Auto"** para reproducción automática.
6. Usa **"⏮ Reset"** para reiniciar.
7. Ajusta la **velocidad** con el slider (Lento ↔ Rápido).

### Demostraciones didácticas

- **Test 'AAAA'**: muestra cómo cuatro letras iguales producen cuatro cifrados distintos.
- **Test 'HOLA MUNDO'**: muestra cómo el espacio desincroniza el contexto entre palabras.

### Tabla de traza

La tabla en el panel derecho muestra para cada carácter:
- **Letra Org.**: carácter original (o cifrado si descifras).
- **Pos Ext**: posición final de la aguja exterior (índice + letra).
- **Pos Int**: posición final de la aguja interior (índice + letra).
- **Desfase**: diferencia acumulada entre los discos (Δ).
- **Letra Cif.**: carácter producido por el mecanismo.
