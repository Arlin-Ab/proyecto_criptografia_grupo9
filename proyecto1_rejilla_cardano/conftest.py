import sys, os

# Múltiples proyectos usan el paquete 'logica/', Python cachea el primero en sys.modules.
# Al cambiar de proyecto se limpia la caché para que se cargue la versión correcta.
for _k in list(sys.modules.keys()):
    if _k == "logica" or _k.startswith("logica."):
        del sys.modules[_k]

_proyecto_root = os.path.dirname(os.path.abspath(__file__))
if _proyecto_root not in sys.path:
    sys.path.insert(0, _proyecto_root)
