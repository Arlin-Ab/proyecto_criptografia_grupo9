# main.py - Punto de entrada del Proyecto 4: Polybios con Clave
#
# Ejecutar con:
#   cd proyecto4_polybios_con_clave
#   python main.py

from interfaz.ventana import AplicacionPolybiosClave


def main():
    app = AplicacionPolybiosClave()
    app.mainloop()


if __name__ == "__main__":
    main()

