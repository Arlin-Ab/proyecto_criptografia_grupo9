# test_steganografia.py — Pruebas unitarias del Proyecto 2: Esteganografía
# Ejecutar con:  pytest tests/test_steganografia.py -v

import sys
import os
import pytest

# Limpiar caché de 'logica' para evitar conflicto con otros proyectos del workspace
for _k in list(sys.modules.keys()):
    if _k == "logica" or _k.startswith("logica."):
        del sys.modules[_k]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logica.steganografia import (
    validar_rejilla,
    generar_rejilla_valida,
    ocultar_mensaje,
    revelar_mensaje,
    obtener_posiciones_lineales,
    texto_a_parrafo,
    parrafo_a_chars,
)


# ──────────────────────────────────────────────
# Pruebas de la rejilla
# ──────────────────────────────────────────────

class TestRejilla:

    def test_rejilla_generada_es_valida(self):
        for n in (4, 6, 8):
            huecos = generar_rejilla_valida(n)
            valida, msg = validar_rejilla(huecos, n)
            assert valida, f"Rejilla inválida para n={n}: {msg}"

    def test_rejilla_vacia_invalida(self):
        valida, msg = validar_rejilla(set(), 4)
        assert not valida
        assert msg

    def test_numero_de_huecos_correcto(self):
        """Una rejilla n×n válida tiene exactamente n²/4 huecos."""
        for n in (4, 6, 8):
            huecos = generar_rejilla_valida(n)
            assert len(huecos) == (n * n) // 4

    def test_posiciones_lineales_ordenadas(self):
        huecos = {(0, 2), (1, 0), (0, 0)}
        posiciones = obtener_posiciones_lineales(huecos, 4)
        assert posiciones == sorted(posiciones)


# ──────────────────────────────────────────────
# Pruebas de ocultar mensaje
# ──────────────────────────────────────────────

class TestOcultar:

    def setup_method(self):
        self.n = 4
        self.huecos = generar_rejilla_valida(self.n)

    def test_ocultar_devuelve_chars_de_longitud_correcta(self):
        chars, _, _, _ = ocultar_mensaje("HOLA", self.huecos, self.n)
        assert len(chars) == self.n * self.n

    def test_letras_secretas_en_posiciones_correctas(self):
        """Las letras del secreto deben aparecer en las posiciones de los huecos."""
        secreto = "HOLA"
        chars, posiciones, _, _ = ocultar_mensaje(secreto, self.huecos, self.n)
        for i, pos in enumerate(posiciones):
            if i < len(secreto):
                assert chars[pos] == secreto[i].upper()

    def test_modo_automatico_no_falla_con_mensaje_vacio(self):
        """Mensaje vacío no debe lanzar excepción."""
        chars, posiciones, _, advertencias = ocultar_mensaje("", self.huecos, self.n)
        assert len(chars) == self.n * self.n
        assert isinstance(advertencias, list)

    def test_mensaje_mayor_capacidad_se_recorta(self):
        """Si el mensaje supera la capacidad, se advierte y recorta."""
        capacidad = len(self.huecos)
        mensaje_largo = "A" * (capacidad + 10)
        _, _, msg_usado, advertencias = ocultar_mensaje(mensaje_largo, self.huecos, self.n)
        assert len(msg_usado) <= capacidad
        assert any("recortado" in adv.lower() or "recort" in adv.lower() for adv in advertencias)

    def test_modo_manual_inserta_letras_correctamente(self):
        """Con texto manual el sistema reemplaza posiciones de huecos."""
        cobertura = "ABCDEFGHIJKLMNOP"  # 16 letras para 4×4
        chars, posiciones, _, _ = ocultar_mensaje("HI", self.huecos, self.n,
                                                   texto_manual=cobertura)
        assert chars[posiciones[0]] == "H"
        assert chars[posiciones[1]] == "I"

    def test_ocultar_solo_acepta_letras(self):
        """Caracteres especiales deben ignorarse; el resultado solo contiene letras."""
        _, _, _, _ = ocultar_mensaje("H3LL0 W0RLD!", self.huecos, self.n)
        # Las letras efectivas son HLLWRLD (7 letras)
        _, _, msg, _ = ocultar_mensaje("H3LL0 W0RLD!", self.huecos, self.n)
        assert msg.isalpha() and msg == msg.upper()


# ──────────────────────────────────────────────
# Pruebas de revelar mensaje
# ──────────────────────────────────────────────

class TestRevelar:

    def setup_method(self):
        self.n = 4
        self.huecos = generar_rejilla_valida(self.n)

    def test_revelar_recupera_mensaje_original(self):
        """ocultar → revelar debe recuperar el secreto."""
        secreto = "CLAVE"
        chars, _, msg_usado, _ = ocultar_mensaje(secreto, self.huecos, self.n)
        texto_cobertura = ''.join(chars)
        mensaje_rev, _, _, error = revelar_mensaje(texto_cobertura, self.huecos, self.n)
        assert error is None
        assert mensaje_rev.startswith(msg_usado)

    def test_revelar_con_texto_insuficiente_da_error(self):
        """Si el texto de cobertura es muy corto, debe retornar error."""
        _, _, _, error = revelar_mensaje("AB", self.huecos, self.n)
        assert error is not None

    def test_revelar_ignora_espacios(self):
        """Los espacios en el texto de cobertura deben ignorarse."""
        chars, _, msg_usado, _ = ocultar_mensaje("OK", self.huecos, self.n)
        texto_con_espacios = texto_a_parrafo(chars, self.n, palabras=True)
        mensaje_rev, _, _, error = revelar_mensaje(texto_con_espacios, self.huecos, self.n)
        assert error is None
        assert mensaje_rev.startswith(msg_usado[:2])

    def test_revelar_posiciones_correctas(self):
        """Las posiciones reveladas deben coincidir con las de ocultar."""
        chars, pos_ocultar, _, _ = ocultar_mensaje("AB", self.huecos, self.n)
        texto = ''.join(chars)
        _, pos_revelar, _, _ = revelar_mensaje(texto, self.huecos, self.n)
        assert pos_ocultar == pos_revelar


# ──────────────────────────────────────────────
# Pruebas de formato de texto
# ──────────────────────────────────────────────

class TestFormato:

    def test_texto_a_parrafo_longitud_correcta(self):
        chars = list("ABCDEFGHIJKLMNOP")  # 16 chars
        parrafo = texto_a_parrafo(chars, 4, palabras=False)
        assert parrafo == "ABCDEFGHIJKLMNOP"

    def test_parrafo_a_chars_solo_letras(self):
        parrafo = "Hola, esto es un texto."
        chars = parrafo_a_chars(parrafo)
        assert all(c.isalpha() for c in chars)
        assert all(c == c.upper() for c in chars)

    def test_parrafo_a_chars_elimina_espacios(self):
        chars = parrafo_a_chars("A B C D")
        assert chars == ["A", "B", "C", "D"]


# ──────────────────────────────────────────────
# Pruebas de casos borde
# ──────────────────────────────────────────────

class TestCasosBorde:

    def test_n6_ida_vuelta(self):
        n = 6
        huecos = generar_rejilla_valida(n)
        secreto = "ATAQUE"
        chars, _, msg_usado, _ = ocultar_mensaje(secreto, huecos, n)
        texto = ''.join(chars)
        revelado, _, _, error = revelar_mensaje(texto, huecos, n)
        assert error is None
        assert revelado.startswith(msg_usado)

    def test_caracter_unico(self):
        n = 4
        huecos = generar_rejilla_valida(n)
        chars, _, _, _ = ocultar_mensaje("X", huecos, n)
        assert len(chars) == n * n

    def test_rejilla_invalida_no_rompe_ocultar(self):
        """Con rejilla inválida, ocultar debe retornar advertencia, no crash."""
        # Rejilla inválida: huecos vacíos
        chars, posiciones, msg, advs = ocultar_mensaje("HOLA", set(), 4)
        # Puede retornar lista vacía de posiciones
        assert isinstance(chars, list)
