# test_polybios.py — Pruebas unitarias del Proyecto 3: Polybios Personalizable
# Ejecutar con:  pytest tests/test_polybios.py -v

import sys
import os
import pytest

for _k in list(sys.modules.keys()):
    if _k == "logica" or _k.startswith("logica."):
        del sys.modules[_k]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logica.polybios import (
    PRESET_5x5_IJ,
    PRESET_5x5_NÑ,
    PRESET_6x6,
    construir_mapa,
    validar_grid,
    aleatorizar_grid,
    cifrar,
    descifrar,
    clonar_grid,
)


# ──────────────────────────────────────────────
# Pruebas de validación de cuadrícula
# ──────────────────────────────────────────────

class TestValidacion:

    def test_presets_son_validos(self):
        """Los tres presets predefinidos deben ser cuadrículas válidas."""
        for grid in (PRESET_5x5_IJ, PRESET_5x5_NÑ, PRESET_6x6):
            valida, msg = validar_grid(grid)
            assert valida, f"Preset inválido: {msg}"

    def test_celda_vacia_invalida(self):
        grid = clonar_grid(PRESET_5x5_IJ)
        grid[0][0] = ""
        valida, msg = validar_grid(grid)
        assert not valida
        assert msg

    def test_caracter_duplicado_invalido(self):
        grid = clonar_grid(PRESET_5x5_IJ)
        grid[0][1] = "A"  # A ya está en (0,0)
        valida, msg = validar_grid(grid)
        assert not valida

    def test_grid_aleatorizada_sigue_siendo_valida(self):
        grid = aleatorizar_grid(PRESET_5x5_IJ)
        valida, _ = validar_grid(grid)
        assert valida


# ──────────────────────────────────────────────
# Pruebas de construcción del mapa
# ──────────────────────────────────────────────

class TestMapa:

    def test_mapa_incluye_todas_las_celdas(self):
        mapa = construir_mapa(PRESET_5x5_IJ)
        # 25 celdas únicas + J (fusionada con I)
        assert "A" in mapa
        assert "Z" in mapa
        assert "I" in mapa
        assert "J" in mapa  # fusionada, debe apuntar al mismo lugar que I
        assert mapa["I"] == mapa["J"]

    def test_mapa_6x6_incluye_digitos(self):
        mapa = construir_mapa(PRESET_6x6)
        assert "0" in mapa
        assert "9" in mapa


# ──────────────────────────────────────────────
# Pruebas de cifrado
# ──────────────────────────────────────────────

class TestCifrado:

    def test_cifrar_hola_coordenadas_correctas(self):
        """HOLA con preset 5×5 IJ debe producir coordenadas conocidas."""
        cifrado, pasos, omit = cifrar("HOLA", PRESET_5x5_IJ)
        # H→(2,3)=23, O→(3,4)=34, L→(3,1)=31, A→(1,1)=11
        assert cifrado == "23 34 31 11"
        assert omit == []

    def test_cifrar_texto_vacio(self):
        cifrado, pasos, omit = cifrar("", PRESET_5x5_IJ)
        assert cifrado == ""
        assert pasos == []

    def test_cifrar_devuelve_pares_correctos(self):
        cifrado, pasos, _ = cifrar("ABC", PRESET_5x5_IJ)
        tokens = cifrado.split()
        assert len(tokens) == 3
        for t in tokens:
            assert len(t) == 2
            assert t.isdigit()

    def test_cifrar_minusculas_igual_que_mayusculas(self):
        c1, _, _ = cifrar("hola", PRESET_5x5_IJ)
        c2, _, _ = cifrar("HOLA", PRESET_5x5_IJ)
        assert c1 == c2

    def test_cifrar_omite_caracteres_no_en_grid(self):
        _, _, omit = cifrar("HOLA!", PRESET_5x5_IJ)
        assert "!" in omit

    def test_cifrar_con_6x6_incluye_digitos(self):
        cifrado, _, omit = cifrar("A1B2", PRESET_6x6)
        assert omit == []
        assert len(cifrado.split()) == 4

    def test_cifrar_j_igual_que_i(self):
        """J e I deben producir las mismas coordenadas (fusión)."""
        c_i, _, _ = cifrar("I", PRESET_5x5_IJ)
        c_j, _, _ = cifrar("J", PRESET_5x5_IJ)
        assert c_i == c_j

    def test_pasos_contienen_info_correcta(self):
        _, pasos, _ = cifrar("A", PRESET_5x5_IJ)
        assert len(pasos) == 1
        paso = pasos[0]
        assert "letra" in paso
        assert "fila" in paso
        assert "col" in paso
        assert "coord" in paso


# ──────────────────────────────────────────────
# Pruebas de descifrado
# ──────────────────────────────────────────────

class TestDescifrado:

    def test_descifrar_coordenadas_conocidas(self):
        """23 34 31 11 con 5×5 IJ debe dar HOLA."""
        desc, _, errores = descifrar("23 34 31 11", PRESET_5x5_IJ)
        assert desc == "HOLA"
        assert errores == []

    def test_descifrar_texto_vacio(self):
        desc, pasos, _ = descifrar("", PRESET_5x5_IJ)
        assert desc == ""
        assert pasos == []

    def test_descifrar_acepta_comas(self):
        """Formato 11,12,13 debe funcionar igual que 11 12 13."""
        d1, _, _ = descifrar("11 12 13", PRESET_5x5_IJ)
        d2, _, _ = descifrar("11,12,13", PRESET_5x5_IJ)
        assert d1 == d2

    def test_descifrar_token_invalido_reporta_error(self):
        _, _, errores = descifrar("11 99 12", PRESET_5x5_IJ)
        assert "99" in errores  # 99 está fuera de rango

    def test_descifrar_token_longitud_incorrecta(self):
        _, _, errores = descifrar("11 1 12", PRESET_5x5_IJ)
        assert "1" in errores


# ──────────────────────────────────────────────
# Pruebas de ida y vuelta (round-trip)
# ──────────────────────────────────────────────

class TestIDAVuelta:

    @pytest.mark.parametrize("grid,texto", [
        (PRESET_5x5_IJ, "HOLAMUNDO"),
        (PRESET_5x5_NÑ, "CRIPTOGRAFIA"),
        (PRESET_6x6,    "SECRETO123"),
    ])
    def test_cifrar_descifrar_ida_vuelta(self, grid, texto):
        cifrado, _, _ = cifrar(texto, grid)
        desc, _, errores = descifrar(cifrado, grid)
        assert errores == []
        # Las celdas fusionadas (IJ) pueden hacer que I→I, J→I: normalizar
        assert desc.replace("J", "I") == texto.replace("J", "I")

    def test_grid_aleatorizado_ida_vuelta(self):
        grid = aleatorizar_grid(PRESET_5x5_IJ)
        cifrado, _, _ = cifrar("PRUEBA", grid)
        desc, _, _ = descifrar(cifrado, grid)
        assert desc.replace("J", "I") == "PRUEBA"
