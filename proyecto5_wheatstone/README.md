# Proyecto 5 – Criptógrafo de Wheatstone

## ¿Qué es el Criptógrafo de Wheatstone?

Es un dispositivo electromecánico de cifrado inventado por Charles Wheatstone en 1867. A diferencia del cifrado de sustitución simple (donde 'A' siempre se cifra como 'M'), el dispositivo de Wheatstone produce una **sustitución poligráfica**. Esto significa que si cifras la letra 'A' cuatro veces seguidas ("AAAA"), la letra resultante será diferente en cada ocasión.

### Funcionamiento

Consta de dos discos concéntricos con agujas como las de un reloj:
*   **Disco Exterior:** Contiene 27 posiciones (A-Z + Espacio `_`). Se usa para buscar la letra del texto plano.
*   **Disco Interior:** Contiene 26 posiciones (A-Z). Indica la letra cifrada.

Ambas agujas están unidas por un mecanismo de engranajes. Cuando la aguja exterior avanza un paso, la aguja interior también avanza un paso. Como tienen tamaños diferentes (27 vs 26 posiciones), cada vuelta produce un **desfase**. Además, el uso de espacios (que ocupa una posición en el disco exterior pero no en el interior) altera dinámicamente la clave para la siguiente palabra.

## Requisitos

- Python 3.10 o superior
- Módulos estándar: `tkinter`, `math` (No requiere instalación adicional)

## Cómo ejecutar

```bash
cd proyecto5_wheatstone
python main.py
```

## Cómo usar el simulador

### Cifrado / Descifrado Básico
1. Escribe tu texto en el campo **TEXTO PLANO / CIFRADO**.
2. Presiona **🔒 Iniciar Cifrado** (o Descifrado). La aplicación comenzará automáticamente la animación letra por letra.
3. Usa el botón **▶ Paso a Paso** para animar el cifrado letra por letra. Verás cómo ambas agujas giran juntas, pero como los discos tienen distintas cantidades de letras, se irán desfasando.
4. Opcionalmente, usa **▶▶ Auto** para reproducir toda la animación automáticamente. Puedes ajustar la velocidad con el control deslizante.
5. En la parte inferior, verás una **Traza de Ejecución** que registra la posición matemática de cada letra, el desfase actual y el resultado del cifrado.

### Pruebas Didácticas
El panel cuenta con dos botones especiales de demostración:
*   **Test 'AAAA':** Demuestra cómo el desfase por la diferencia de tamaño de los discos hace que la letra 'A' se cifre de cuatro formas diferentes consecutivas.
*   **Test 'HOLA MUNDO':** Demuestra cómo la presencia de un espacio ' ' (representado como `_` en el disco exterior) consume un movimiento del engranaje sin producir una letra útil, desfasando el alfabeto completo para la siguiente palabra ("MUNDO").

## Estructura del proyecto

```
proyecto5_wheatstone/
├── main.py           ← Punto de entrada de la aplicación
├── engranajes.py     ← Lógica matemática, cálculo de desfases e índices
├── interfaz.py       ← Interfaz gráfica con Tkinter Canvas y animación
└── README.md         ← Este archivo
```
