# main.py - Punto de entrada del Proyecto 5: Criptógrafo de Wheatstone
#
# Ejecutar con:
#   cd proyecto5_wheatstone
#   python main.py

from interfaz.ventana import AplicacionWheatstone

def main():
    app = AplicacionWheatstone()
    app.mainloop()

if __name__ == "__main__":
    main()

