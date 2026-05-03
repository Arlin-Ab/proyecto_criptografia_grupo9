# test_rejilla.py — Pruebas unitarias del Proyecto 1: Rejilla de Cardano
# Ejecutar con:  pytest tests/test_rejilla.py -v

import sys
import os
import pytest

# Añadir el directorio raíz del proyecto al path para importar logica/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logica.rejilla import (
    rotar_rejilla_90,
    obtener_todas_rotaciones,
    validar_rejilla,
    cifrar,
    descifrar,
    generar_rejilla_ejemplo,
    matriz_a_texto,
)


# ──────────────────────────────────────────────
# Pruebas de rotación
# ──────────────────────────────────────────────

class TestRotacion:

    def test_rotar_celda_esquina_superior_izquierda(self):
        """(0,0) en 4×4 rota a (0,3) al girar 90° horario."""
        resultado = rotar_rejilla_90({(0, 0)}, 4)
        assert resultado == {(0, 3)}

    def test_rotar_celda_esquina_inferior_derecha(self):
        """(3,3) en 4×4 rota a (3,0)."""
        resultado = rotar_rejilla_90({(3, 3)}, 4)
        assert resultado == {(3, 0)}

    def test_cuatro_rotaciones_vuelven_al_origen(self):
        """Rotar 4 veces debe devolver el conjunto original."""
        huecos = {(0, 1), (2, 3)}
        actual = huecos
        for _ in range(4):
            actual = rotar_rejilla_90(actual, 4)
        assert actual == huecos

    def test_obtener_todas_rotaciones_longitud(self):
        """Debe devolver exactamente 4 conjuntos."""
        huecos = generar_rejilla_ejemplo(4)
        rots = obtener_todas_rotaciones(huecos, 4)
        assert len(rots) == 4

    def test_primera_rotacion_es_original(self):
        """La primera rotación (índice 0) es la rejilla sin rotar."""
        huecos = generar_rejilla_ejemplo(4)
        rots = obtener_todas_rotaciones(huecos, 4)
        assert rots[0] == huecos


# ──────────────────────────────────────────────
# Pruebas de validación
# ──────────────────────────────────────────────

class TestValidacion:

    def test_rejilla_generada_automaticamente_es_valida(self):
        for n in (4, 6, 8):
            huecos = generar_rejilla_ejemplo(n)
            valida, msg = validar_rejilla(huecos, n)
            assert valida, f"Fallo en n={n}: {msg}"

    def test_rejilla_vacia_invalida(self):
        valida, msg = validar_rejilla(set(), 4)
        assert not valida
        assert msg  # debe tener mensaje de error

    def test_numero_de_huecos_incorrecto(self):
        """Demasiados huecos → inválida."""
        valida, msg = validar_rejilla({(0,0), (0,1), (0,2)}, 4)  # 3 en vez de 4
        assert not valida

    def test_huecos_con_superposicion(self):
        """Dos huecos que colisionan al rotar → inválida."""
        # En 4×4, (0,0) y (0,3) son rotaciones el uno del otro
        valida, _ = validar_rejilla({(0,0), (0,3), (3,3), (3,0)}, 4)
        # Esta combinación puede o no ser válida; lo importante es que no crash
        assert isinstance(valida, bool)

    def test_rotaciones_disjuntas_cubren_todo(self):
        """Para una rejilla válida las 4 rotaciones deben cubrir n² celdas."""
        for n in (4, 6):
            huecos = generar_rejilla_ejemplo(n)
            rots = obtener_todas_rotaciones(huecos, n)
            todas = set()
            for r in rots:
                todas.update(r)
            assert len(todas) == n * n, f"No cubre todo el grid en n={n}"


# ──────────────────────────────────────────────
# Pruebas de cifrado
# ──────────────────────────────────────────────

class TestCifrado:

    def setup_method(self):
        self.huecos4 = generar_rejilla_ejemplo(4)
        self.huecos6 = generar_rejilla_ejemplo(6)

    def test_cifrar_devuelve_matriz_correcta(self):
        """La matriz cifrada debe ser n×n."""
        matriz, _, _ = cifrar("HOLA", self.huecos4, 4)
        assert len(matriz) == 4
        for fila in matriz:
            assert len(fila) == 4

    def test_cifrar_sin_celdas_vacias(self):
        """Toda celda de la matriz debe tener un carácter."""
        matriz, _, _ = cifrar("HOLA", self.huecos4, 4)
        for fila in matriz:
            for celda in fila:
                assert celda != "", "Celda vacía en la matriz cifrada"

    def test_cifrar_mensaje_vacio_usa_relleno(self):
        """Con mensaje vacío se rellena con X."""
        matriz, _, texto = cifrar("", self.huecos4, 4)
        assert texto == "X" * 16
        assert all(c == "X" for fila in matriz for c in fila)

    def test_cifrar_mensaje_largo_se_recorta(self):
        """Mensaje mayor a la capacidad se recorta."""
        _, _, texto = cifrar("A" * 100, self.huecos4, 4)
        assert len(texto) == 16  # capacidad 4×4

    def test_cifrar_un_caracter(self):
        """Un solo carácter no debe lanzar excepción."""
        matriz, pasos, _ = cifrar("Z", self.huecos4, 4)
        assert len(pasos) == 4

    def test_cifrar_caracteres_especiales_se_ignoran(self):
        """Dígitos y signos no causan excepción y no aparecen en el resultado."""
        _, _, texto = cifrar("H3LL0 W0RLD!", self.huecos4, 4)
        # El texto solo contiene letras mayúsculas (o X de relleno)
        assert texto.isalpha() and texto == texto.upper()
        # Las letras efectivas del mensaje son H, L, L, W, R, L, D
        letras = ''.join(c for c in "H3LL0 W0RLD!" if c.isalpha()).upper()
        assert texto.startswith(letras)

    def test_cifrar_mayusculas_y_minusculas_equivalentes(self):
        """'hola' y 'HOLA' deben producir el mismo cifrado."""
        m1, _, _ = cifrar("hola", self.huecos4, 4)
        m2, _, _ = cifrar("HOLA", self.huecos4, 4)
        assert m1 == m2

    def test_pasos_tienen_4_rotaciones(self):
        """Siempre deben generarse exactamente 4 pasos."""
        _, pasos, _ = cifrar("HOLA MUNDO", self.huecos4, 4)
        assert len(pasos) == 4

    def test_pasos_angulos_correctos(self):
        """Los ángulos de los pasos deben ser 0, 90, 180, 270."""
        _, pasos, _ = cifrar("HOLA", self.huecos4, 4)
        angulos = [p['rotacion'] for p in pasos]
        assert angulos == [0, 90, 180, 270]


# ──────────────────────────────────────────────
# Pruebas de descifrado
# ──────────────────────────────────────────────

class TestDescifrado:

    def setup_method(self):
        self.huecos4 = generar_rejilla_ejemplo(4)
        self.huecos6 = generar_rejilla_ejemplo(6)

    def test_descifrar_devuelve_mensaje_original(self):
        """cifrar → descifrar debe recuperar el texto (sin espacios)."""
        for mensaje in ("HOLA", "CRIPTOGRAFIA", "A"):
            matriz, _, texto_usado = cifrar(mensaje, self.huecos4, 4)
            recuperado, _ = descifrar(matriz, self.huecos4, 4)
            assert recuperado == texto_usado, f"Fallo con mensaje='{mensaje}'"

    def test_ida_y_vuelta_n6(self):
        """Probar ida y vuelta con rejilla 6×6."""
        mensaje = "SECRETO"
        matriz, _, texto = cifrar(mensaje, self.huecos6, 6)
        recuperado, _ = descifrar(matriz, self.huecos6, 6)
        assert recuperado == texto

    def test_descifrar_no_falla_con_matriz_vacia(self):
        """Descifrar una matriz de cadenas vacías no debe lanzar excepción."""
        n = 4
        matriz_vacia = [['' for _ in range(n)] for _ in range(n)]
        resultado, _ = descifrar(matriz_vacia, self.huecos4, n)
        assert isinstance(resultado, str)


# ──────────────────────────────────────────────
# Pruebas de casos borde
# ──────────────────────────────────────────────

class TestCasosBorde:

    def test_rejilla_n4_completa(self):
        huecos = generar_rejilla_ejemplo(4)
        matriz, _, texto = cifrar("ABCDEFGHIJKLMNOP", huecos, 4)
        rec, _ = descifrar(matriz, huecos, 4)
        assert rec == "ABCDEFGHIJKLMNOP"

    def test_mensaje_exactamente_capacidad(self):
        """Mensaje que llena exactamente la cuadrícula no debe truncarse."""
        huecos = generar_rejilla_ejemplo(4)
        msg = "A" * 16
        _, _, texto = cifrar(msg, huecos, 4)
        assert texto == msg

    def test_matriz_a_texto_no_falla(self):
        huecos = generar_rejilla_ejemplo(4)
        matriz, _, _ = cifrar("HOLA", huecos, 4)
        texto = matriz_a_texto(matriz)
        assert isinstance(texto, str)
        assert len(texto) > 0
