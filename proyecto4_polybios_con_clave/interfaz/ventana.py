# interfaz.py - Interfaz Gráfica del Proyecto 4: Polybios con Clave
# Muestra la construcción animada de la cuadrícula desde la clave,
# modo comparación (estándar vs clave) y análisis de seguridad.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from logica.polybios_clave import (
    MODOS,
    construir_grid_con_clave,
    grid_estandar,
    cifrar,
    descifrar,
    analisis_seguridad,
    comparar_grids,
    guardar_configuracion,
    cargar_configuracion,
    normalizar_clave,
    eliminar_duplicados,
)

# ──────────────────────────────────────────────
# Paleta de colores
# ──────────────────────────────────────────────
C_FONDO     = "#0f172a"
C_PANEL     = "#1e293b"
C_PANEL2    = "#162032"
C_BORDE     = "#334155"
C_ACENTO    = "#8b5cf6"
C_ACENTO2   = "#22d3ee"
C_EXITO     = "#4ade80"
C_PELIGRO   = "#f87171"
C_ADVERT    = "#fbbf24"
C_TEXTO     = "#e2e8f0"
C_SUB       = "#94a3b8"

C_CELDA     = "#1e293b"
C_CELDA_BRD = "#475569"
C_FUSED     = "#1a3a2a"
C_FUSED_BRD = "#22c55e"
C_CLAVE_BG  = "#4c1d95"    # celda que viene de la clave
C_CLAVE_BRD = "#a78bfa"
C_FILL_BG   = "#0f2941"    # celda de relleno durante construcción
C_FILL_BRD  = "#38bdf8"
C_ACTIVA    = "#fbbf24"    # celda resaltada en animación
C_ACTIVA_BRD= "#fde68a"
C_IGUAL     = "#1e293b"    # celda igual en comparación
C_IGUAL_BRD = "#475569"
C_DIFER_BG  = "#7f1d1d"    # celda diferente en comparación
C_DIFER_BRD = "#fca5a5"

C_BTN       = "#3730a3"
C_BTN2      = "#065f46"    # botón de acción principal (verde)
C_BTN_HOV   = "#4338ca"

TAM         = 56           # tamaño de celda en canvas
PAD         = 12


class AplicacionPolybiosClave(tk.Tk):
    """Ventana principal del cifrador Polybios con clave."""

    def __init__(self):
        super().__init__()
        self.title("Polybios con Clave – Proyecto 4")
        self.configure(bg=C_FONDO)
        self.minsize(1150, 720)
        self.resizable(True, True)

        # Estado
        self._modo_key = tk.StringVar(value='5x5_IJ')
        self._grid_clave = None
        self._grid_std   = None
        self._clave_actual = ""
        self._pasos_constr = []
        self._paso_constr  = 0
        self._animando_c   = False
        self._velocidad    = tk.IntVar(value=600)

        # Pasos cifrado/descifrado
        self._pasos_cif  = []
        self._paso_cif   = 0
        self._animando_f = False
        self._pasos_des  = []
        self._paso_des   = 0
        self._animando_d = False

        self._construir_ui()
        self._actualizar_modo()

    # ──────────────────────────────────────────────
    # Construcción de la UI
    # ──────────────────────────────────────────────

    def _construir_ui(self):
        # Cabecera
        cab = tk.Frame(self, bg=C_FONDO, pady=10)
        cab.pack(fill=tk.X, padx=PAD)
        tk.Label(cab, text="🔑  Polybios con Clave",
                 font=("Segoe UI", 15, "bold"), bg=C_FONDO, fg=C_ACENTO
                 ).pack(side=tk.LEFT)
        tk.Label(cab,
                 text="La clave reorganiza el alfabeto → mismo mensaje, coordenadas distintas",
                 font=("Segoe UI", 10), bg=C_FONDO, fg=C_SUB
                 ).pack(side=tk.LEFT, padx=14)

        # Layout de 3 columnas
        main = tk.Frame(self, bg=C_FONDO)
        main.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD))

        izq = tk.Frame(main, bg=C_PANEL, padx=10, pady=10, width=290)
        izq.pack(side=tk.LEFT, fill=tk.Y)
        izq.pack_propagate(False)
        self._construir_col_izq(izq)

        centro = tk.Frame(main, bg=C_FONDO)
        centro.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        self._construir_col_centro(centro)

        der = tk.Frame(main, bg=C_PANEL, padx=10, pady=10, width=420)
        der.pack(side=tk.LEFT, fill=tk.Y)
        der.pack_propagate(False)
        self._construir_col_der(der)

    # ── Columna izquierda: configuración y cifrado ──

    def _construir_col_izq(self, parent):
        self._lbl_sec(parent, "MODO DE CUADRÍCULA", C_PANEL)
        for key, datos in MODOS.items():
            tk.Radiobutton(
                parent, text=datos['nombre'],
                variable=self._modo_key, value=key,
                command=self._actualizar_modo,
                bg=C_PANEL, fg=C_TEXTO, selectcolor=C_ACENTO,
                activebackground=C_PANEL, font=("Segoe UI", 9)
            ).pack(anchor=tk.W, pady=1)

        self._lbl_sec(parent, "PALABRA CLAVE", C_PANEL)
        tk.Label(parent, text="Ingresa la clave (solo letras):",
                 bg=C_PANEL, fg=C_SUB, font=("Segoe UI", 9)
                 ).pack(anchor=tk.W)

        f_clave = tk.Frame(parent, bg=C_PANEL)
        f_clave.pack(fill=tk.X, pady=4)
        self.entry_clave = tk.Entry(
            f_clave, bg="#ffffff", fg="#0f172a", insertbackground="#0f172a",
            font=("Segoe UI", 13, "bold"), relief=tk.FLAT, width=14
        )
        self.entry_clave.pack(side=tk.LEFT, padx=(0, 4))
        self._setup_entry_placeholder(self.entry_clave, "Ej: CRYPTO")
        self.entry_clave.bind("<Return>", lambda e: self._generar_grid())

        self._btn_destac(f_clave, "⚙ Generar", self._generar_grid, C_BTN2)

        # Clave normalizada (preview)
        self.lbl_clave_norm = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_ACENTO2,
            font=("Courier New", 10), wraplength=240, justify=tk.LEFT
        )
        self.lbl_clave_norm.pack(fill=tk.X, pady=2)

        # Error / validación
        self.lbl_err_clave = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_PELIGRO,
            font=("Segoe UI", 9), wraplength=240, justify=tk.LEFT
        )
        self.lbl_err_clave.pack(fill=tk.X)

        # Guardar / cargar
        self._lbl_sec(parent, "PERSISTENCIA", C_PANEL)
        f_gc = tk.Frame(parent, bg=C_PANEL)
        f_gc.pack(fill=tk.X, pady=2)
        self._btn_s(f_gc, "💾 Guardar", self._guardar, tk.LEFT)
        self._btn_s(f_gc, "📂 Cargar",  self._cargar,  tk.LEFT)

        # ── Cifrado ──
        self._lbl_sec(parent, "CIFRAR / DESCIFRAR", C_PANEL)
        tk.Label(parent, text="Texto plano:", bg=C_PANEL, fg=C_TEXTO,
                 font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.entry_plano = tk.Text(
            parent, height=3, bg="#ffffff", fg="#0f172a",
            insertbackground="#0f172a", font=("Segoe UI", 10),
            relief=tk.FLAT, padx=6, pady=4
        )
        self.entry_plano.pack(fill=tk.X, pady=(2, 4))
        self._setup_text_placeholder(self.entry_plano, "Ej: HOLA o 23 34 31 11")

        f_b = tk.Frame(parent, bg=C_PANEL)
        f_b.pack(fill=tk.X, pady=2)
        self._btn_s(f_b, "🔒 Cifrar",   self._cifrar,   tk.LEFT)
        self._btn_s(f_b, "🔓 Descifrar", self._descifrar, tk.LEFT)

        # Resultado
        self._lbl_sec(parent, "RESULTADO", C_PANEL)
        self.lbl_resultado = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_ACENTO2,
            font=("Courier New", 12, "bold"), wraplength=250, justify=tk.LEFT
        )
        self.lbl_resultado.pack(anchor=tk.W, pady=2)
        self.lbl_omitidos = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_ADVERT,
            font=("Segoe UI", 8), wraplength=250
        )
        self.lbl_omitidos.pack(anchor=tk.W)

    # ── Columna central: cuadrícula principal ──

    def _construir_col_centro(self, parent):
        # Título de la cuadrícula activa
        self.lbl_titulo_grid = tk.Label(
            parent, text="CUADRÍCULA CON CLAVE",
            bg=C_FONDO, fg=C_ACENTO,
            font=("Segoe UI", 11, "bold")
        )
        self.lbl_titulo_grid.pack(anchor=tk.W)
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(2, 8))

        # Canvas de la cuadrícula principal
        f_canvas = tk.Frame(parent, bg=C_FONDO)
        f_canvas.pack()

        self.canvas_main = tk.Canvas(f_canvas, bg=C_FONDO, highlightthickness=0)
        self.canvas_main.pack()

        # Leyenda
        leyenda = tk.Frame(parent, bg=C_FONDO)
        leyenda.pack(anchor=tk.W, pady=4)
        self._leyenda(leyenda, C_CLAVE_BG,  C_CLAVE_BRD, "Letra de la clave")
        self._leyenda(leyenda, C_FILL_BG,   C_FILL_BRD,  "Relleno alfabético")

        # Tabla de pasos de cifrado/descifrado
        self._lbl_sec_fondo(parent, "PASOS DEL CIFRADO / DESCIFRADO", C_FONDO)
        self._construir_tabla_pasos(parent)

    def _construir_tabla_pasos(self, parent):
        """Tabla de pasos del cifrado o descifrado."""
        f = tk.Frame(parent, bg=C_FONDO)
        f.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("P4.Treeview",
                        background=C_PANEL, foreground=C_TEXTO,
                        fieldbackground=C_PANEL, rowheight=22,
                        font=("Courier New", 9))
        style.configure("P4.Treeview.Heading",
                        background=C_ACENTO, foreground="#fff",
                        font=("Segoe UI", 9, "bold"))
        style.map("P4.Treeview", background=[("selected", "#0891b2")])

        sb = tk.Scrollbar(f, bg=C_PANEL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("Letra", "Celda", "Fila", "Col", "Coord")
        self.tabla = ttk.Treeview(
            f, columns=cols, show="headings",
            style="P4.Treeview", height=8,
            yscrollcommand=sb.set
        )
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=75, anchor=tk.CENTER)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self.tabla.yview)

    # ── Columna derecha: comparación y seguridad ──

    def _construir_col_der(self, parent):
        style = ttk.Style()
        style.configure("P4.TNotebook", background=C_PANEL, borderwidth=0)
        style.configure("P4.TNotebook.Tab", background=C_PANEL2,
                        foreground=C_TEXTO, padding=(10, 5),
                        font=("Segoe UI", 9))
        style.map("P4.TNotebook.Tab",
                  background=[("selected", C_ACENTO)],
                  foreground=[("selected", "#fff")])

        nb = ttk.Notebook(parent, style="P4.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True)

        tab_comp = tk.Frame(nb, bg=C_PANEL, padx=8, pady=8)
        nb.add(tab_comp, text="⚖  Comparación")
        self._construir_tab_comparacion(tab_comp)

        tab_seg = tk.Frame(nb, bg=C_PANEL, padx=8, pady=8)
        nb.add(tab_seg, text="🔐  Seguridad")
        self._construir_tab_seguridad(tab_seg)

    def _construir_tab_comparacion(self, parent):
        """Dos cuadrículas apiladas verticalmente: estándar (arriba) vs con clave (abajo)."""
        # Área con scroll para que quepan grids grandes
        canvas_scroll = tk.Canvas(parent, bg=C_PANEL, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas_scroll.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas_scroll.configure(yscrollcommand=sb.set)

        inner = tk.Frame(canvas_scroll, bg=C_PANEL)
        win_id = canvas_scroll.create_window((0, 0), window=inner, anchor=tk.NW)

        def _resize(e):
            canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
            canvas_scroll.itemconfig(win_id, width=e.width)
        inner.bind("<Configure>", _resize)
        canvas_scroll.bind("<Configure>", lambda e: canvas_scroll.itemconfig(win_id, width=e.width))
        canvas_scroll.bind_all("<MouseWheel>",
            lambda e: canvas_scroll.yview_scroll(int(-1*(e.delta/120)), "units"))

        tk.Label(inner,
                 text="  🟥 Rojo = posición distinta a la estándar  "
                      " 🟦 Azul = posición igual",
                 bg=C_PANEL, fg=C_SUB, font=("Segoe UI", 8), wraplength=360
                 ).pack(anchor=tk.W, pady=(0, 6))

        # ── Cuadrícula estándar ──
        tk.Label(inner, text="CUADRÍCULA ESTÁNDAR (sin clave)",
                 bg=C_PANEL, fg=C_SUB,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(6, 0))
        tk.Frame(inner, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(2, 4))
        self.canvas_std = tk.Canvas(inner, bg=C_FONDO, highlightthickness=0)
        self.canvas_std.pack(anchor=tk.W, pady=(0, 8))

        # ── Cuadrícula con clave ──
        tk.Label(inner, text="CUADRÍCULA CON CLAVE",
                 bg=C_PANEL, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(6, 0))
        tk.Frame(inner, bg=C_ACENTO, height=1).pack(fill=tk.X, pady=(2, 4))
        self.canvas_clave = tk.Canvas(inner, bg=C_FONDO, highlightthickness=0)
        self.canvas_clave.pack(anchor=tk.W, pady=(0, 8))

        # ── Texto cifrado comparativo ──
        tk.Label(inner, text="MISMO TEXTO → DISTINTO RESULTADO",
                 bg=C_PANEL, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(6, 2))
        tk.Frame(inner, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 4))

        f_cifs = tk.Frame(inner, bg=C_PANEL)
        f_cifs.pack(fill=tk.X)

        # Estándar
        f_s = tk.Frame(f_cifs, bg=C_PANEL2, pady=6)
        f_s.pack(fill=tk.X, pady=2)
        tk.Label(f_s, text="Estándar:", bg=C_PANEL2, fg=C_SUB,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=8)
        # Text de solo lectura → se adapta al ancho del frame automáticamente
        self.lbl_cif_std = tk.Text(
            f_s, height=3, bg=C_PANEL2, fg=C_TEXTO,
            font=("Courier New", 11, "bold"),
            relief=tk.FLAT, wrap=tk.WORD,
            padx=8, pady=4, state=tk.DISABLED,
            cursor="arrow"
        )
        self.lbl_cif_std.pack(fill=tk.X, padx=4)

        # Con clave
        f_c = tk.Frame(f_cifs, bg=C_PANEL2, pady=6)
        f_c.pack(fill=tk.X, pady=2)
        tk.Label(f_c, text="Con clave:", bg=C_PANEL2, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=8)
        self.lbl_cif_clave = tk.Text(
            f_c, height=3, bg=C_PANEL2, fg=C_ACENTO2,
            font=("Courier New", 11, "bold"),
            relief=tk.FLAT, wrap=tk.WORD,
            padx=8, pady=4, state=tk.DISABLED,
            cursor="arrow"
        )
        self.lbl_cif_clave.pack(fill=tk.X, padx=4)

    def _construir_tab_seguridad(self, parent):
        """Panel de análisis de seguridad."""
        self.lbl_seg = tk.Label(
            parent, text="Genera una cuadrícula\npara ver el análisis.",
            bg=C_PANEL, fg=C_SUB,
            font=("Segoe UI", 10), justify=tk.LEFT, wraplength=290
        )
        self.lbl_seg.pack(anchor=tk.W, pady=8)

        # Barra visual de entropía
        self._lbl_sec(parent, "ENTROPÍA EN BITS", C_PANEL)
        self.canvas_entropia = tk.Canvas(
            parent, bg=C_CELDA, height=30, highlightthickness=0
        )
        self.canvas_entropia.pack(fill=tk.X, pady=4)

        # Comparativa con estándares conocidos
        self._lbl_sec(parent, "COMPARATIVA", C_PANEL)
        comparativa = [
            ("DES",         56,   C_PELIGRO),
            ("3DES",        112,  C_ADVERT),
            ("AES-128",     128,  C_EXITO),
            ("AES-256",     256,  C_EXITO),
        ]
        self.lbl_comparativa = {}
        for nombre, bits_ref, color in comparativa:
            f = tk.Frame(parent, bg=C_PANEL)
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=f"{nombre}:", bg=C_PANEL, fg=color,
                     font=("Segoe UI", 9, "bold"), width=10,
                     anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(f, text=f"{bits_ref} bits", bg=C_PANEL, fg=C_TEXTO,
                     font=("Courier New", 9)).pack(side=tk.LEFT)
            self.lbl_comparativa[nombre] = tk.Label(
                f, text="", bg=C_PANEL, fg=color,
                font=("Segoe UI", 8)
            )
            self.lbl_comparativa[nombre].pack(side=tk.LEFT, padx=4)

        self.lbl_bits_polybios = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_ACENTO2,
            font=("Segoe UI", 10, "bold")
        )
        self.lbl_bits_polybios.pack(anchor=tk.W, pady=6)

        self._lbl_sec(parent, "IMPORTANCIA DE LA CLAVE", C_PANEL)
        self.lbl_explicacion = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_TEXTO,
            font=("Segoe UI", 9), wraplength=290, justify=tk.LEFT
        )
        self.lbl_explicacion.pack(anchor=tk.W)

    # ──────────────────────────────────────────────
    # Helpers de UI
    # ──────────────────────────────────────────────

    def _lbl_sec(self, parent, texto, bg):
        tk.Label(parent, text=texto, bg=bg, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(8, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 4))

    def _lbl_sec_fondo(self, parent, texto, bg):
        tk.Label(parent, text=texto, bg=bg, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(10, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 4))

    def _btn_s(self, parent, texto, cmd, side):
        b = tk.Button(parent, text=texto, command=cmd,
                      bg=C_BTN, fg=C_TEXTO,
                      activebackground=C_BTN_HOV, activeforeground=C_TEXTO,
                      font=("Segoe UI", 9), relief=tk.FLAT,
                      padx=6, pady=4, cursor="hand2")
        b.pack(side=side, padx=2, pady=1)

    def _btn_destac(self, parent, texto, cmd, bg_color):
        b = tk.Button(parent, text=texto, command=cmd,
                      bg=bg_color, fg="#ffffff",
                      activebackground=bg_color, activeforeground="#ffffff",
                      font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
                      padx=8, pady=5, cursor="hand2")
        b.pack(side=tk.LEFT)

    def _leyenda(self, parent, bg, borde, texto):
        f = tk.Frame(parent, bg=parent.cget("bg"))
        f.pack(side=tk.LEFT, padx=6)
        c = tk.Canvas(f, width=16, height=16, bg=parent.cget("bg"), highlightthickness=0)
        c.pack(side=tk.LEFT)
        c.create_rectangle(1, 1, 15, 15, fill=bg, outline=borde, width=2)
        tk.Label(f, text=texto, bg=parent.cget("bg"), fg=C_SUB,
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=2)

    def _setup_entry_placeholder(self, entry, texto):
        """Configura placeholder básico para Entry."""
        entry.placeholder_text = texto
        entry.placeholder_activo = True
        entry.config(fg=C_SUB)
        entry.delete(0, tk.END)
        entry.insert(0, texto)
        entry.bind("<FocusIn>", lambda e: self._entry_focus_in(e.widget))
        entry.bind("<FocusOut>", lambda e: self._entry_focus_out(e.widget))

    def _entry_focus_in(self, entry):
        if getattr(entry, "placeholder_activo", False):
            entry.delete(0, tk.END)
            entry.config(fg="#0f172a")
            entry.placeholder_activo = False

    def _entry_focus_out(self, entry):
        if not entry.get().strip():
            entry.delete(0, tk.END)
            entry.insert(0, entry.placeholder_text)
            entry.config(fg=C_SUB)
            entry.placeholder_activo = True

    def _setup_text_placeholder(self, text_widget, texto):
        """Configura placeholder básico para Text."""
        text_widget.placeholder_text = texto
        text_widget.placeholder_activo = True
        text_widget.config(fg=C_SUB)
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", texto)
        text_widget.bind("<FocusIn>", lambda e: self._text_focus_in(e.widget))
        text_widget.bind("<FocusOut>", lambda e: self._text_focus_out(e.widget))

    def _text_focus_in(self, text_widget):
        if getattr(text_widget, "placeholder_activo", False):
            text_widget.delete("1.0", tk.END)
            text_widget.config(fg="#0f172a")
            text_widget.placeholder_activo = False

    def _text_focus_out(self, text_widget):
        contenido = text_widget.get("1.0", tk.END).strip()
        if not contenido:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", text_widget.placeholder_text)
            text_widget.config(fg=C_SUB)
            text_widget.placeholder_activo = True

    def _get_entry_value(self, entry):
        """Obtiene valor real del Entry ignorando placeholder."""
        if getattr(entry, "placeholder_activo", False):
            return ""
        return entry.get().strip()

    def _get_text_value(self, text_widget):
        """Obtiene valor real del Text ignorando placeholder."""
        if getattr(text_widget, "placeholder_activo", False):
            return ""
        return text_widget.get("1.0", tk.END).strip()

    def _celda_label_display(self, celda):
        """Etiqueta visual de celda según el modo (ej. I -> IJ en 5x5 IJ)."""
        if not celda:
            return ""
        modo_key = self._modo_key.get()
        display_map = MODOS.get(modo_key, {}).get('celda_display', {})
        return display_map.get(celda, celda)

    def _token_descifrado_display(self, celda):
        """
        Formatea la letra descifrada para mostrar ambigüedades en celdas fusionadas.
        Ejemplo: 'IJ' -> 'I/J' o 'I' (que se visualiza como 'IJ') -> 'I/J'
        """
        label = self._celda_label_display(celda)
        if len(label) > 1:
            return "/".join(label)
        return label

    # ──────────────────────────────────────────────
    # Dibujo de cuadrículas
    # ──────────────────────────────────────────────

    def _dibujar_canvas(self, canvas, grid, modo_key,
                        paso_idx=-1, mascara_diff=None, tam=None):
        """
        Dibuja una cuadrícula en el canvas indicado.

        paso_idx   : si >= 0, muestra solo las celdas hasta ese índice
                     (para la animación de construcción)
        mascara_diff: máscara booleana para resaltar diferencias
        tam        : tamaño de celda (override)
        """
        canvas.delete("all")
        n      = len(grid)
        t      = tam or TAM
        ox, oy = PAD + 16, PAD + 16
        modo   = MODOS[modo_key]
        display = modo['celda_display']
        pasos  = self._pasos_constr

        # Etiquetas de columna y fila
        for j in range(n):
            canvas.create_text(ox + j * t + t // 2, oy - 10,
                               text=str(j + 1), fill=C_SUB,
                               font=("Segoe UI", 9, "bold"))
        for i in range(n):
            canvas.create_text(ox - 10, oy + i * t + t // 2,
                               text=str(i + 1), fill=C_SUB,
                               font=("Segoe UI", 9, "bold"))

        # Celdas
        for i in range(n):
            for j in range(n):
                x1 = ox + j * t
                y1 = oy + i * t
                x2, y2 = x1 + t, y1 + t
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                pos    = i * n + j
                celda  = grid[i][j]
                label  = display.get(celda, celda)
                es_fusion = len(celda) > 1 or celda != label

                # Determinar color
                if paso_idx >= 0 and pos == paso_idx:
                    # Celda siendo colocada ahora
                    fill  = C_ACTIVA
                    borde = C_ACTIVA_BRD
                    grosor = 3
                    color_txt = "#0f172a"
                elif paso_idx >= 0 and pos > paso_idx:
                    # Celda aún no colocada
                    fill  = "#0a0f1a"
                    borde = "#1e293b"
                    grosor = 1
                    canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2,
                                            fill=fill, outline=borde, width=1)
                    continue
                elif mascara_diff is not None:
                    if mascara_diff[i][j]:
                        fill  = C_IGUAL
                        borde = C_IGUAL_BRD
                    else:
                        fill  = C_DIFER_BG
                        borde = C_DIFER_BRD
                    grosor = 2
                    color_txt = "#ffffff"
                elif paso_idx >= 0 and pasos and pos < len(pasos):
                    origen = pasos[pos]['origen'] if pos < len(pasos) else 'relleno'
                    if origen == 'clave':
                        fill  = C_CLAVE_BG
                        borde = C_CLAVE_BRD
                    else:
                        fill  = C_FILL_BG
                        borde = C_FILL_BRD
                    grosor = 2
                    color_txt = "#ffffff"
                else:
                    # Vista normal sin animación
                    if pasos and pos < len(pasos):
                        origen = pasos[pos]['origen']
                        fill  = C_CLAVE_BG if origen == 'clave' else (
                            C_FUSED if es_fusion else C_CELDA)
                        borde = C_CLAVE_BRD if origen == 'clave' else (
                            C_FUSED_BRD if es_fusion else C_CELDA_BRD)
                    else:
                        fill  = C_FUSED if es_fusion else C_CELDA
                        borde = C_FUSED_BRD if es_fusion else C_CELDA_BRD
                    grosor = 1 if not pasos else 2
                    color_txt = "#ffffff"

                canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2,
                                        fill=fill, outline=borde, width=grosor)
                fs = 13 if len(label) == 1 else 9
                canvas.create_text(cx, cy, text=label,
                                   fill=color_txt,
                                   font=("Segoe UI", fs, "bold"))

        ancho = ox * 2 + n * t
        alto  = oy * 2 + n * t
        canvas.config(width=ancho, height=alto)

    def _dibujar_main(self, paso_idx=-1, resaltar_cif=None):
        if self._grid_clave is None:
            return
        if resaltar_cif is not None:
            # Resaltar celda del cifrado
            grid  = self._grid_clave
            n     = len(grid)
            modo  = self._modo_key.get()
            self.canvas_main.delete("all")
            pasos_backup = self._pasos_constr
            self._pasos_constr = []
            self._dibujar_canvas(self.canvas_main, grid, modo)
            self._pasos_constr = pasos_backup

            # Redibujar solo la celda activa con resaltado
            fi, col = resaltar_cif
            t  = TAM
            ox, oy = PAD + 16, PAD + 16
            x1 = ox + col * t
            y1 = oy + fi  * t
            x2, y2 = x1 + t, y1 + t
            display = MODOS[modo]['celda_display']
            celda   = grid[fi][col]
            label   = display.get(celda, celda)
            self.canvas_main.create_rectangle(
                x1+2, y1+2, x2-2, y2-2,
                fill=C_ACTIVA, outline=C_ACTIVA_BRD, width=3
            )
            self.canvas_main.create_text(
                (x1+x2)/2, (y1+y2)/2, text=label,
                fill="#0f172a", font=("Segoe UI", 13, "bold")
            )
        else:
            self._dibujar_canvas(
                self.canvas_main, self._grid_clave,
                self._modo_key.get(), paso_idx
            )

    def _dibujar_comparacion(self):
        if self._grid_clave is None or self._grid_std is None:
            return
        modo_key = self._modo_key.get()
        mascara  = comparar_grids(self._grid_std, self._grid_clave, modo_key)

        # Tamaño de celda para comparación: suficientemente grande para leer
        t_comp = 44

        # Guardamos y limpiamos pasos para que no afecten el coloreo de comparación
        pasos_backup       = self._pasos_constr
        self._pasos_constr = []

        # Cuadrícula estándar: rojo donde DIFIERE de la versión con clave
        mascara_std = [[not v for v in fila] for fila in mascara]
        self._dibujar_canvas(self.canvas_std, self._grid_std,
                             modo_key, tam=t_comp, mascara_diff=mascara_std)

        # Cuadrícula con clave: rojo donde DIFIERE de la estándar
        mascara_clave = [[not v for v in fila] for fila in mascara]
        self._dibujar_canvas(self.canvas_clave, self._grid_clave,
                             modo_key, tam=t_comp, mascara_diff=mascara_clave)

        self._pasos_constr = pasos_backup

        # Cifrado comparativo
        texto = self._get_text_value(self.entry_plano)
        
        def _actualizar_txt(widget, contenido):
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", contenido)
            widget.config(state=tk.DISABLED)

        if texto:
            c_std,   _, _ = cifrar(texto, self._grid_std,   modo_key)
            c_clave, _, _ = cifrar(texto, self._grid_clave, modo_key)
            _actualizar_txt(self.lbl_cif_std, c_std or "—")
            _actualizar_txt(self.lbl_cif_clave, c_clave or "—")
        else:
            _actualizar_txt(self.lbl_cif_std, "—")
            _actualizar_txt(self.lbl_cif_clave, "—")

    def _actualizar_seguridad(self):
        modo_key = self._modo_key.get()
        stats    = analisis_seguridad(modo_key)
        n        = stats['n']
        bits     = stats['bits_entropia']
        notacion = stats['notacion_cientifica']

        txt = (
            f"Cuadrícula {n}×{n} = {n*n} celdas\n\n"
            f"Permutaciones posibles:\n  {notacion}\n\n"
            f"Entropía máxima:  {bits:.1f} bits"
        )
        self.lbl_seg.config(text=txt)

        # Barra de entropía
        self.canvas_entropia.delete("all")
        max_bits = 300
        ancho    = min(int(bits / max_bits * 280), 280)
        color    = C_EXITO if bits > 128 else (C_ADVERT if bits > 56 else C_PELIGRO)
        self.canvas_entropia.create_rectangle(0, 0, 280, 30, fill=C_CELDA, outline="")
        self.canvas_entropia.create_rectangle(0, 0, ancho, 30, fill=color, outline="")
        self.canvas_entropia.create_text(
            140, 15, text=f"{bits:.1f} bits",
            fill="#ffffff", font=("Segoe UI", 10, "bold")
        )
        self.canvas_entropia.config(width=280, height=30)

        # Comparativa
        etiquetas = {
            "DES":    (56,   "< DES (inseguro)"),
            "3DES":   (112,  "equivalente a 3DES"),
            "AES-128":(128,  "equivalente a AES-128"),
            "AES-256":(256,  "equivalente a AES-256"),
        }
        for nombre, (bits_ref, desc) in etiquetas.items():
            if bits >= bits_ref:
                self.lbl_comparativa[nombre].config(text=f"✓ supera ({bits:.0f}>{bits_ref})")
            else:
                self.lbl_comparativa[nombre].config(text=f"✗ ({bits:.0f}<{bits_ref})")

        self.lbl_bits_polybios.config(text=f"Polybios {n}×{n}: {bits:.1f} bits")

        explicacion = (
            f"Sin clave: el atacante solo necesita probar la cuadrícula estándar.\n\n"
            f"Con una clave de k letras únicas: el orden de las primeras k celdas "
            f"varía, incrementando el espacio de búsqueda.\n\n"
            f"⚠ Polybios NO es seguro para uso real — solo es didáctico. "
            f"La entropía teórica ({bits:.0f} bits) asume que el atacante no sabe la clave; "
            f"con análisis de frecuencias puede romperlo."
        )
        self.lbl_explicacion.config(text=explicacion)

    # ──────────────────────────────────────────────
    # Acciones principales
    # ──────────────────────────────────────────────

    def _actualizar_modo(self):
        """Regenera la cuadrícula estándar al cambiar de modo."""
        modo_key        = self._modo_key.get()
        self._grid_std  = grid_estandar(modo_key)
        self._grid_clave = None
        self._pasos_constr = []
        self.canvas_main.delete("all")
        self._actualizar_seguridad()

    def _generar_grid(self):
        clave    = self._get_entry_value(self.entry_clave)
        modo_key = self._modo_key.get()

        # Mostrar clave normalizada (preview)
        clave_norm = eliminar_duplicados(normalizar_clave(clave, modo_key))
        self.lbl_clave_norm.config(
            text=f"Clave normalizada: {''.join(clave_norm)}"
        )

        grid, pasos, error = construir_grid_con_clave(clave, modo_key)
        if error:
            self.lbl_err_clave.config(text=f"✗ {error}")
            return

        self.lbl_err_clave.config(text="✓ Cuadrícula generada")
        self._grid_clave    = grid
        self._clave_actual  = clave
        self._pasos_constr  = pasos
        self._paso_constr   = len(pasos) - 1  # mostrar cuadrícula completa por defecto
        self._animando_c    = False

        # Título con la clave
        self.lbl_titulo_grid.config(
            text=f'CUADRÍCULA CON CLAVE  "{clave.upper()}"'
        )

        self._dibujar_main()
        self._dibujar_comparacion()
        self._actualizar_seguridad()

    # ── Animación de construcción ──

    def _paso_constr_btn(self):
        if not self._pasos_constr:
            messagebox.showinfo("Sin pasos", "Genera una cuadrícula primero.")
            return
        n_pasos = len(self._pasos_constr)
        if self._paso_constr >= n_pasos - 1:
            self._paso_constr = -1
        self._paso_constr += 1
        self._dibujar_main(paso_idx=self._paso_constr)

    def _reset_constr(self):
        self._paso_constr = len(self._pasos_constr) - 1
        self._animando_c  = False
        self._dibujar_main()

    def _animar_constr(self):
        if not self._pasos_constr:
            messagebox.showinfo("Sin pasos", "Genera una cuadrícula primero.")
            return
        if self._animando_c:
            return
        self._animando_c  = True
        self._paso_constr = -1
        self._tick_constr()

    def _tick_constr(self):
        if not self._animando_c:
            return
        self._paso_constr += 1
        if self._paso_constr >= len(self._pasos_constr):
            self._animando_c = False
            self._dibujar_main()   # mostrar cuadrícula completa con colores
            return
        self._dibujar_main(paso_idx=self._paso_constr)
        self.after(self._velocidad.get(), self._tick_constr)

    # ── Cifrado ──

    def _cifrar(self):
        if self._grid_clave is None:
            messagebox.showwarning("Sin cuadrícula", "Genera una cuadrícula con clave primero.")
            return
        texto = self._get_text_value(self.entry_plano)
        if not texto:
            messagebox.showwarning("Sin texto", "Ingresa el texto a cifrar.")
            return

        modo_key = self._modo_key.get()
        cifrado, pasos, omit = cifrar(texto, self._grid_clave, modo_key)
        self._pasos_cif  = pasos
        self._paso_cif   = 0
        self._animando_f = False

        self.lbl_resultado.config(text=cifrado)
        self.lbl_omitidos.config(
            text=f"⚠ Omitidos: {''.join(set(omit))}" if omit else ""
        )
        self._poblar_tabla(pasos, modo='cifrar')
        self._dibujar_comparacion()

    def _paso_cif_btn(self):
        if not self._pasos_cif:
            messagebox.showinfo("Sin pasos", "Cifra un texto primero.")
            return
        if self._paso_cif >= len(self._pasos_cif):
            self._paso_cif = 0
        paso = self._pasos_cif[self._paso_cif]
        self._dibujar_main(resaltar_cif=(paso['fila'], paso['col']))
        self._resaltar_tabla(self._paso_cif)
        self._paso_cif += 1

    def _reset_cif(self):
        self._paso_cif   = 0
        self._animando_f = False
        self._dibujar_main()

    def _animar_cif(self):
        if not self._pasos_cif:
            messagebox.showinfo("Sin pasos", "Cifra un texto primero.")
            return
        if self._animando_f:
            return
        self._animando_f = True
        self._paso_cif   = 0
        self._tick_cif()

    def _tick_cif(self):
        if not self._animando_f:
            return
        if self._paso_cif >= len(self._pasos_cif):
            self._animando_f = False
            self._dibujar_main()
            return
        paso = self._pasos_cif[self._paso_cif]
        self._dibujar_main(resaltar_cif=(paso['fila'], paso['col']))
        self._resaltar_tabla(self._paso_cif)
        self._paso_cif += 1
        self.after(self._velocidad.get(), self._tick_cif)

    # ── Descifrado ──

    def _descifrar(self):
        if self._grid_clave is None:
            messagebox.showwarning("Sin cuadrícula", "Genera una cuadrícula con clave primero.")
            return
        texto_c = self._get_text_value(self.entry_plano)
        if not texto_c:
            messagebox.showwarning("Sin texto", "Ingresa las coordenadas a descifrar.")
            return

        descifrado, pasos, errores = descifrar(texto_c, self._grid_clave)
        self._pasos_des  = pasos
        self._paso_des   = 0
        self._animando_d = False

        # En celdas fusionadas (ej. IJ), mostramos ambigüedad explícita: I/J
        tokens_display = [self._token_descifrado_display(p['celda']) for p in pasos]
        descifrado_display = " ".join(tokens_display) if tokens_display else descifrado
        self.lbl_resultado.config(text=f"Descifrado: {descifrado_display}")
        self.lbl_omitidos.config(
            text=f"⚠ Tokens no reconocidos: {', '.join(errores)}" if errores else ""
        )
        self._poblar_tabla(pasos, modo='descifrar')

    # ── Tabla de pasos ──

    def _poblar_tabla(self, pasos, modo):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        if modo == 'cifrar':
            for p in pasos:
                self.tabla.insert("", tk.END, values=(
                    p['letra'], self._celda_label_display(p['celda']),
                    p['fila']+1, p['col']+1, p['coord']
                ))
        else:
            for p in pasos:
                self.tabla.insert("", tk.END, values=(
                    p['coord'], self._celda_label_display(p['celda']),
                    p['fila']+1, p['col']+1,
                    self._token_descifrado_display(p['celda'])
                ))

    def _resaltar_tabla(self, idx):
        children = self.tabla.get_children()
        if idx < len(children):
            self.tabla.selection_set(children[idx])
            self.tabla.see(children[idx])

    # ── Guardar / cargar ──

    def _guardar(self):
        if self._grid_clave is None:
            messagebox.showwarning("Sin cuadrícula", "Genera una cuadrícula primero.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Guardar configuración"
        )
        if ruta:
            guardar_configuracion(
                self._grid_clave, self._clave_actual,
                self._modo_key.get(), ruta
            )
            messagebox.showinfo("Guardado", f"Configuración guardada en:\n{ruta}")

    def _cargar(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Cargar configuración"
        )
        if ruta:
            try:
                grid, clave, modo_key = cargar_configuracion(ruta)
                self._modo_key.set(modo_key)
                self.entry_clave.delete(0, tk.END)
                self.entry_clave.insert(0, clave)
                self.entry_clave.config(fg="#0f172a")
                self.entry_clave.placeholder_activo = False
                self._actualizar_modo()
                self._generar_grid()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar:\n{e}")

