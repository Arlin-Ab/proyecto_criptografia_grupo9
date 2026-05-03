# main.py - Punto de entrada del Proyecto 2: Esteganografía con Rejilla de Cardano

from interfaz.ventana import AplicacionEsteganografia


def main():
    app = AplicacionEsteganografia()
    app.mainloop()


if __name__ == "__main__":
    main()

