# test_polybios_clave.py — Pruebas del Proyecto 4: Polybios con Clave
# Ejecutar con:  pytest tests/test_polybios_clave.py -v

import sys
import os
import pytest

for _k in list(sys.modules.keys()):
    if _k == "logica" or _k.startswith("logica."):
        del sys.modules[_k]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logica.polybios_clave import (
    MODOS,
    eliminar_duplicados,
    normalizar_clave,
    construir_secuencia,
    construir_grid_con_clave,
    grid_estandar,
    cifrar,
    descifrar,
    analisis_seguridad,
    comparar_grids,
)


# ──────────────────────────────────────────────
# Pruebas de procesamiento de clave
# ──────────────────────────────────────────────

class TestProcesamiento:

    def test_eliminar_duplicados_preserva_orden(self):
        assert eliminar_duplicados(list("AABCCA")) == list("ABC")

    def test_eliminar_duplicados_lista_vacia(self):
        assert eliminar_duplicados([]) == []

    def test_normalizar_clave_mayusculas(self):
        resultado = normalizar_clave("crypto", "5x5_IJ")
        assert resultado == list("CRYPTO")

    def test_normalizar_j_a_i_en_modo_ij(self):
        """En modo 5×5 IJ, la J debe mapearse a I."""
        resultado = normalizar_clave("JOKE", "5x5_IJ")
        assert "J" not in resultado
        assert resultado[0] == "I"  # J→I

    def test_normalizar_descarta_chars_invalidos(self):
        """Dígitos y signos no deben aparecer en 5×5."""
        resultado = normalizar_clave("H3L!O", "5x5_IJ")
        assert all(c.isalpha() for c in resultado)

    def test_normalizar_6x6_acepta_digitos(self):
        resultado = normalizar_clave("A1B2", "6x6")
        assert "1" in resultado
        assert "2" in resultado


# ──────────────────────────────────────────────
# Pruebas de construcción de cuadrícula
# ──────────────────────────────────────────────

class TestConstruccion:

    def test_grid_crypto_primera_fila_correcta(self):
        """La clave CRYPTO debe poner C,R,Y,P,T en la primera fila."""
        grid, _, err = construir_grid_con_clave("CRYPTO", "5x5_IJ")
        assert err is None
        assert grid[0] == ["C", "R", "Y", "P", "T"]

    def test_grid_crypto_segunda_fila_empieza_con_O(self):
        grid, _, _ = construir_grid_con_clave("CRYPTO", "5x5_IJ")
        assert grid[1][0] == "O"

    def test_grid_tamano_correcto_5x5(self):
        grid, _, err = construir_grid_con_clave("CLAVE", "5x5_IJ")
        assert err is None
        assert len(grid) == 5
        assert all(len(fila) == 5 for fila in grid)

    def test_grid_tamano_correcto_6x6(self):
        grid, _, err = construir_grid_con_clave("SECRETO", "6x6")
        assert err is None
        assert len(grid) == 6
        assert all(len(fila) == 6 for fila in grid)

    def test_grid_clave_vacia_da_error(self):
        _, _, err = construir_grid_con_clave("", "5x5_IJ")
        assert err is not None

    def test_grid_clave_invalida_da_error(self):
        """Una clave con solo dígitos (no válidos en 5×5) debe dar error."""
        _, _, err = construir_grid_con_clave("12345", "5x5_IJ")
        assert err is not None

    def test_grid_estandar_orden_alfabetico(self):
        """La cuadrícula estándar debe tener A en (0,0)."""
        grid = grid_estandar("5x5_IJ")
        assert grid[0][0] == "A"

    def test_grid_con_clave_difiere_del_estandar(self):
        """La cuadrícula con clave CRYPTO NO debe ser igual a la estándar."""
        grid_c, _, _ = construir_grid_con_clave("CRYPTO", "5x5_IJ")
        grid_s = grid_estandar("5x5_IJ")
        assert grid_c != grid_s

    def test_pasos_construccion_longitud_correcta(self):
        """Los pasos deben cubrir todas las n² posiciones."""
        _, pasos, _ = construir_grid_con_clave("CRYPTO", "5x5_IJ")
        assert len(pasos) == 25

    def test_pasos_distinguen_clave_de_relleno(self):
        _, pasos, _ = construir_grid_con_clave("CRYPTO", "5x5_IJ")
        origenes = {p['origen'] for p in pasos}
        assert 'clave' in origenes
        assert 'relleno' in origenes


# ──────────────────────────────────────────────
# Pruebas de cifrado / descifrado
# ──────────────────────────────────────────────

class TestCifrado:

    def setup_method(self):
        self.grid, _, _ = construir_grid_con_clave("CRYPTO", "5x5_IJ")
        self.modo = "5x5_IJ"

    def test_cifrar_texto_vacio(self):
        c, pasos, omit = cifrar("", self.grid, self.modo)
        assert c == ""
        assert pasos == []

    def test_cifrar_devuelve_pares(self):
        c, _, _ = cifrar("HOLA", self.grid, self.modo)
        tokens = c.split()
        assert len(tokens) == 4

    def test_cifrar_con_clave_distinto_al_estandar(self):
        """La misma letra debe producir coordenadas distintas según la clave."""
        grid_std = grid_estandar(self.modo)
        c_clave, _, _ = cifrar("HOLA", self.grid, self.modo)
        c_std,   _, _ = cifrar("HOLA", grid_std, self.modo)
        assert c_clave != c_std

    def test_descifrar_texto_vacio(self):
        d, pasos, _ = descifrar("", self.grid)
        assert d == ""
        assert pasos == []

    def test_ida_vuelta_5x5(self):
        c, _, _ = cifrar("CRIPTOGRAFIA", self.grid, self.modo)
        d, _, _ = descifrar(c, self.grid)
        assert d.replace("J", "I") == "CRIPTOGRAFIA"

    @pytest.mark.parametrize("clave,modo", [
        ("PYTHON",  "5x5_IJ"),
        ("SEGURO",  "5x5_NÑ"),
        ("DATOS12", "6x6"),
    ])
    def test_ida_vuelta_varios_modos(self, clave, modo):
        grid, _, err = construir_grid_con_clave(clave, modo)
        assert err is None
        texto = "MENSAJE"
        c, _, _ = cifrar(texto, grid, modo)
        d, _, _ = descifrar(c, grid)
        assert d.replace("J", "I") == texto.replace("J", "I")


# ──────────────────────────────────────────────
# Pruebas de análisis de seguridad
# ──────────────────────────────────────────────

class TestSeguridad:

    def test_analisis_5x5_bits_positivos(self):
        stats = analisis_seguridad("5x5_IJ")
        assert stats['bits_entropia'] > 0

    def test_analisis_6x6_mas_seguro_que_5x5(self):
        s5 = analisis_seguridad("5x5_IJ")
        s6 = analisis_seguridad("6x6")
        assert s6['bits_entropia'] > s5['bits_entropia']

    def test_comparar_grids_mismo_grid_todo_igual(self):
        grid = grid_estandar("5x5_IJ")
        mascara = comparar_grids(grid, grid, "5x5_IJ")
        assert all(v for fila in mascara for v in fila)

    def test_comparar_grids_crypto_vs_estandar(self):
        g_std = grid_estandar("5x5_IJ")
        g_clave, _, _ = construir_grid_con_clave("CRYPTO", "5x5_IJ")
        mascara = comparar_grids(g_std, g_clave, "5x5_IJ")
        # Debe haber algunas diferencias
        hay_diferencias = any(not v for fila in mascara for v in fila)
        assert hay_diferencias
