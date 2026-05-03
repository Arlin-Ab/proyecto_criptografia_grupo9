# test_wheatstone.py — Pruebas del Proyecto 5: Criptógrafo de Wheatstone
# Ejecutar con:  pytest tests/test_wheatstone.py -v

import sys
import os
import pytest

for _k in list(sys.modules.keys()):
    if _k == "logica" or _k.startswith("logica."):
        del sys.modules[_k]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logica.engranajes import (
    DISCO_EXT,
    DISCO_INT,
    normalizar_texto,
    calcular_avance,
    cifrar_wheatstone,
    descifrar_wheatstone,
    simular_caso_aaaa,
    simular_caso_espacio,
)


# ──────────────────────────────────────────────
# Pruebas de constantes del mecanismo
# ──────────────────────────────────────────────

class TestConstantes:

    def test_disco_exterior_27_posiciones(self):
        assert len(DISCO_EXT) == 27

    def test_disco_interior_26_posiciones(self):
        assert len(DISCO_INT) == 26

    def test_disco_exterior_contiene_espacio(self):
        assert "_" in DISCO_EXT

    def test_disco_interior_solo_letras(self):
        assert all(c.isalpha() for c in DISCO_INT)

    def test_disco_exterior_contiene_todas_letras(self):
        for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert letra in DISCO_EXT


# ──────────────────────────────────────────────
# Pruebas de normalización
# ──────────────────────────────────────────────

class TestNormalizacion:

    def test_minusculas_a_mayusculas(self):
        assert normalizar_texto("hola") == "HOLA"

    def test_espacio_a_guion_bajo(self):
        assert normalizar_texto("A B") == "A_B"

    def test_caracteres_invalidos_eliminados(self):
        # ',' y '.' no están en DISCO_EXT
        result = normalizar_texto("H,O.L.A")
        assert "," not in result
        assert "." not in result

    def test_texto_vacio(self):
        assert normalizar_texto("") == ""


# ──────────────────────────────────────────────
# Pruebas del cálculo de avance
# ──────────────────────────────────────────────

class TestAvance:

    def test_avance_nunca_es_cero(self):
        """Si ya estamos en la posición objetivo, debe avanzar una vuelta."""
        for i in range(27):
            avance = calcular_avance(i, DISCO_EXT[i], DISCO_EXT)
            assert avance == 27  # vuelta completa

    def test_avance_positivo(self):
        avance = calcular_avance(0, "B", DISCO_EXT)
        assert avance > 0

    def test_avance_ciclico(self):
        """El avance siempre debe ser ≤ len(alfabeto)."""
        for i in range(27):
            for j in range(27):
                avance = calcular_avance(i, DISCO_EXT[j], DISCO_EXT)
                assert 1 <= avance <= 27


# ──────────────────────────────────────────────
# Pruebas del cifrado de Wheatstone
# ──────────────────────────────────────────────

class TestCifrado:

    def test_cifrar_texto_vacio(self):
        resultado, pasos = cifrar_wheatstone("")
        assert resultado == ""
        assert pasos == []

    def test_cifrar_un_caracter(self):
        resultado, pasos = cifrar_wheatstone("A")
        assert len(resultado) == 1
        assert resultado.isalpha()
        assert len(pasos) == 1

    def test_cifrar_longitud_igual_entrada(self):
        """El cifrado debe tener la misma longitud que el texto normalizado."""
        texto = "HOLA MUNDO"
        resultado, pasos = cifrar_wheatstone(texto)
        texto_norm = normalizar_texto(texto)
        assert len(resultado) == len(texto_norm)
        assert len(pasos) == len(texto_norm)

    def test_cifrar_solo_produce_letras(self):
        """El texto cifrado solo debe contener letras A-Z."""
        resultado, _ = cifrar_wheatstone("CRIPTOGRAFIA")
        assert resultado.isalpha()

    def test_pasos_contienen_campos_requeridos(self):
        _, pasos = cifrar_wheatstone("AB")
        for paso in pasos:
            assert "letra_clara" in paso
            assert "letra_cifrada" in paso
            assert "avance" in paso
            assert "pos_ext_post" in paso
            assert "pos_int_post" in paso


# ──────────────────────────────────────────────
# Pruebas del descifrado de Wheatstone
# ──────────────────────────────────────────────

class TestDescifrado:

    def test_descifrar_texto_vacio(self):
        resultado, pasos = descifrar_wheatstone("")
        assert resultado == ""
        assert pasos == []

    def test_ida_vuelta_basico(self):
        """cifrar → descifrar debe recuperar el texto original."""
        texto = "HOLA"
        cifrado, pasos_c = cifrar_wheatstone(texto)
        # Descifrar usando las posiciones finales del cifrado → no directamente
        # El descifrado debe iniciarse desde las mismas posiciones iniciales
        descifrado, _ = descifrar_wheatstone(cifrado)
        # Recuperar el texto original (puede incluir espacios convertidos a _)
        texto_norm = normalizar_texto(texto)
        assert descifrado == texto_norm

    def test_ida_vuelta_con_espacios(self):
        texto = "HOLA MUNDO"
        cifrado, _ = cifrar_wheatstone(texto)
        descifrado, _ = descifrar_wheatstone(cifrado)
        assert descifrado == normalizar_texto(texto)

    def test_descifrar_longitud_correcta(self):
        cifrado, _ = cifrar_wheatstone("SECRETO")
        descifrado, _ = descifrar_wheatstone(cifrado)
        assert len(descifrado) == len(cifrado)


# ──────────────────────────────────────────────
# Pruebas de propiedades del mecanismo
# ──────────────────────────────────────────────

class TestPropiedadesMecanismo:

    def test_aaaa_produce_letras_distintas(self):
        """Cuatro A seguidas deben producir 4 letras cifradas distintas."""
        cifrado, _ = cifrar_wheatstone("AAAA")
        assert len(set(cifrado)) > 1, (
            "Las repeticiones de 'A' deberían cifrarse distinto cada vez"
        )

    def test_desfase_acumulativo(self):
        """Con letras repetidas (A), el desfase interno crece en cada paso."""
        # Cada 'A' requiere avance=27 (vuelta completa): p_ext queda en 0, p_int avanza 1
        # → el desfase (p_ext - p_int) varía en cada repetición
        _, pasos = cifrar_wheatstone("AAAA")
        desfases = [(p['pos_ext_post'] - p['pos_int_post']) % 26 for p in pasos]
        assert len(set(desfases)) > 1

    def test_espacio_genera_paso_adicional(self):
        """El espacio cuenta como un carácter en el procesamiento."""
        _, pasos_sin = cifrar_wheatstone("HOLAMUNDO")
        _, pasos_con = cifrar_wheatstone("HOLA MUNDO")
        assert len(pasos_con) == len(pasos_sin) + 1

    def test_simular_caso_aaaa(self):
        resultado = simular_caso_aaaa()
        assert len(resultado) == 4
        assert len(set(resultado)) > 1

    def test_simular_caso_espacio(self):
        resultado = simular_caso_espacio()
        # "HOLA_MUNDO" → 10 chars (con espacio→_)
        assert len(resultado) == 10

    def test_posiciones_se_actualizan_en_cada_paso(self):
        """Cada paso debe actualizar las posiciones de los discos."""
        _, pasos = cifrar_wheatstone("AB")
        assert pasos[0]['pos_ext_post'] != pasos[1]['pos_ext_post'] or \
               pasos[0]['pos_int_post'] != pasos[1]['pos_int_post']
