# conftest.py raiz - permite ejecutar todos los tests desde aqui
import sys, os
root = os.path.dirname(__file__)
for nombre in os.listdir(root):
    ruta = os.path.join(root, nombre)
    if os.path.isdir(ruta) and nombre.startswith("proyecto"):
        sys.path.insert(0, ruta)
