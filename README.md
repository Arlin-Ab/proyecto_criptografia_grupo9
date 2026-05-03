# Proyecto de Criptografía Clásica — Grupo 9

Cinco implementaciones de algoritmos de criptografía clásica en Python con interfaz gráfica Tkinter.

## Proyectos

| # | Nombre | Algoritmo | Ejecutar |
|---|--------|-----------|---------|
| 1 | Rejilla de Cardano | Cifrado por rejilla giratoria (4 rotaciones) | `cd proyecto1_rejilla_cardano && python main.py` |
| 2 | Esteganografía | Ocultación de mensajes en texto de cobertura | `cd proyecto2_esteganografia && python main.py` |
| 3 | Polybios personalizado | Coordenadas en cuadrícula con drag & drop | `cd proyecto3_polybios_personalizado && python main.py` |
| 4 | Polybios con clave | Cuadrícula reordenada por palabra clave | `cd proyecto4_polybios_con_clave && python main.py` |
| 5 | Wheatstone | Discos concéntricos con desfase mecánico 27/26 | `cd proyecto5_wheatstone && python main.py` |

## Requisitos

- Python 3.10 o superior
- Tkinter (incluido en Python estándar)
- pytest (solo para ejecutar tests): `pip install -r requirements.txt`

## Estructura de cada proyecto

```
proyectoN_nombre/
├── main.py              ← Punto de entrada
├── logica/
│   └── *.py             ← Algoritmo puro, sin UI
├── interfaz/
│   └── ventana.py       ← Interfaz gráfica Tkinter
├── tests/
│   └── test_*.py        ← Pruebas con pytest
└── docs/
    └── documentacion.md ← Documentación técnica completa
```

## Ejecutar los tests

```bash
# Tests de un proyecto específico
cd proyecto1_rejilla_cardano
python -m pytest tests/ -v

# Todos los tests del proyecto
python -m pytest proyecto1_rejilla_cardano/tests/ proyecto2_esteganografia/tests/ proyecto3_polybios_personalizado/tests/ proyecto4_polybios_con_clave/tests/ proyecto5_wheatstone/tests/ -v
```
