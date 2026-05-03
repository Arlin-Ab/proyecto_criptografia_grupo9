# Proyecto 4 – Cifrador Polybios con Clave

## ¿Qué es el cifrado Polybios con Clave?

El cifrado Polybios estándar codifica cada letra como un par de coordenadas `(fila, columna)` en una cuadrícula. La variante **con clave** reorganiza el orden de las letras en la cuadrícula usando una palabra secreta:

1. Se toma la palabra clave y se eliminan letras repetidas
2. Esas letras ocupan las primeras posiciones de la cuadrícula
3. El resto del alfabeto (en orden) completa las posiciones restantes

**Ejemplo con clave `CRYPTO` en 5×5:**

```
    1  2  3  4  5
1   C  R  Y  P  T
2   O  A  B  D  E
3   F  G  H  I/J K
4   L  M  N  Q  S
5   U  V  W  X  Z
```

La letra **H** se cifra como `33` (fila 3, columna 3).  
Sin clave, **H** sería `23`. La misma letra → coordenadas distintas → mayor seguridad.

## Requisitos

- Python 3.10 o superior
- No requiere librerías externas (usa solo `tkinter`, incluido en Python)

## Cómo ejecutar

```bash
cd proyecto4_polybios_con_clave
python main.py
```

## Modos de cuadrícula disponibles

| Modo | Tamaño | Alfabeto |
|------|--------|----------|
| `5×5 (I/J fusionados, sin Ñ)` | 25 símbolos | A–Z sin J (J→I) |
| `5×5 (I/J fusionados, con Ñ, sin W)` | 25 símbolos | A–Z con Ñ, sin J ni W |
| `6×6 (letras + dígitos 0-9)` | 36 símbolos | A–Z con Ñ + 0–9 |

## Cómo usar la aplicación

### 1. Configurar el modo
Selecciona el **modo de cuadrícula** en el panel izquierdo según el tipo de texto que vayas a cifrar.

### 2. Generar la cuadrícula con clave
1. Escribe tu **palabra clave** en el campo correspondiente (solo letras; se ignoran números y símbolos)
2. Haz clic en **⚙ Generar**
3. La cuadrícula aparece en el centro, con las letras de la clave resaltadas en **morado** y el relleno en **azul**
4. Usa **▶ Paso** o **▶▶ Auto** para ver la animación de construcción letra por letra

### 3. Cifrar un mensaje
1. Escribe el texto en el campo **Texto plano**
2. Haz clic en **🔒 Cifrar**
3. El resultado aparece en la sección **RESULTADO** como pares de coordenadas (ej. `33 11 42`)
4. Usa **▶ Paso** para ver cómo cada letra se mapea a sus coordenadas en la cuadrícula

### 4. Descifrar un mensaje
1. Pega las coordenadas cifradas en el campo **Texto plano** (pares de 2 dígitos separados por espacios)
2. Haz clic en **🔓 Descifrar**
3. El mensaje original aparece en **RESULTADO**

### 5. Modo comparación _(pestaña derecha)_
- Muestra lado a lado la cuadrícula **estándar** vs la cuadrícula **con clave**
- Las celdas en **rojo** son las posiciones que difieren
- Cifra el mismo texto con ambas cuadrículas para ver que producen resultados distintos

### 6. Análisis de seguridad _(pestaña derecha)_
- Muestra el número total de cuadrículas posibles (permutaciones de `n²` símbolos)
- Expresa la entropía en bits y la compara con estándares modernos (DES, AES…)
- Explica por qué Polybios es didáctico pero no apto para uso real

### 7. Guardar y cargar configuraciones
- **💾 Guardar** exporta la clave y la cuadrícula a un archivo `.json`
- **📂 Cargar** recupera una configuración guardada previamente

## Restricción matemática

Para que la cuadrícula sea válida, el número de símbolos únicos de la clave más el relleno alfabético debe ser exactamente `n²`. Los caracteres de la clave que no pertenecen al modo elegido son ignorados automáticamente.

## Estructura del proyecto

```
proyecto4_polybios_con_clave/
├── main.py           ← Punto de entrada (ejecutar este)
├── polybios_clave.py ← Lógica: construcción, cifrado, descifrado, análisis
├── interfaz.py       ← Interfaz gráfica (Tkinter)
└── README.md         ← Este archivo
```

## Ejemplo de uso completo

| Paso | Acción | Resultado |
|------|--------|-----------|
| Clave: `CRYPTO` | Generar cuadrícula | C,R,Y,P,T,O al inicio |
| Texto: `HOLA` | Cifrar | `33 35 31 11` (con clave) |
| Texto: `HOLA` | Cifrar sin clave | `23 35 31 11` (estándar) |
| Coordenadas: `33 35 31 11` | Descifrar | `HOLA` |
