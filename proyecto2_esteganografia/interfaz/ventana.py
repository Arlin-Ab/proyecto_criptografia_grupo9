# interfaz.py - Interfaz Gráfica del Proyecto 2: Esteganografía con Rejilla de Cardano
# Tkinter + Canvas para el editor de rejilla + widget Text con resaltado

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from logica.steganografia import (
    validar_rejilla,
    generar_rejilla_valida,
    ocultar_mensaje,
    revelar_mensaje,
    chars_a_texto_resaltado,
    texto_a_parrafo,
    parrafo_a_chars,
    guardar_configuracion,
    cargar_configuracion,
    obtener_posiciones_lineales,
)

# ──────────────────────────────────────────────
# Paleta de colores
# ──────────────────────────────────────────────
C_FONDO        = "#0f172a"
C_PANEL        = "#1e293b"
C_PANEL2       = "#162032"
C_BORDE        = "#334155"
C_ACENTO       = "#8b5cf6"
C_ACENTO2      = "#22d3ee"
C_EXITO        = "#4ade80"
C_PELIGRO      = "#f87171"
C_ADVERTENCIA  = "#fbbf24"
C_TEXTO        = "#e2e8f0"
C_TEXTO_SUB    = "#94a3b8"
C_CELDA        = "#1e293b"
C_CELDA_BORDE  = "#475569"
C_HUECO        = "#7c3aed"
C_HUECO_BORDE  = "#a78bfa"
C_ROTACION     = "#0f3a2e"
C_ROTACION_BORDE = "#10b981"
C_SECRETO_BG   = "#7c3aed"   # fondo de letra secreta en el Text widget
C_SECRETO_FG   = "#ffffff"   # letra secreta
C_NORMAL_BG    = "#1e293b"   # fondo de letra normal
C_NORMAL_FG    = "#cbd5e1"   # letra normal
C_BTN          = "#3730a3"
C_BTN_HOVER    = "#4338ca"
TAM_CELDA      = 52
PAD            = 16


class AplicacionEsteganografia(tk.Tk):
    """Ventana principal del simulador de esteganografía."""

    def __init__(self):
        super().__init__()
        self.title("Esteganografía con Rejilla de Cardano – Proyecto 2")
        self.configure(bg=C_FONDO)
        self.minsize(1050, 680)
        self.resizable(True, True)

        # Estado
        self.n = tk.IntVar(value=4)
        self.huecos = set()
        self.huecos_rotados = set()
        self._rotaciones_por_angulo = {}
        self.mostrar_resaltado = tk.BooleanVar(value=True)
        self._chars_actuales = []       # lista de n² chars del resultado
        self._posiciones_actuales = []  # posiciones secretas actuales

        # Animación paso a paso
        self._pasos_animacion = []
        self._paso_actual = -1
        self._job_auto = None
        self._celda_activa_anim = None
        self._auto_corriendo = False

        # Fix limitación 3: texto original del usuario en "Revelar"
        self._texto_original_revelar = ""

        self._construir_ui()
        self._dibujar_rejilla()

    # ──────────────────────────────────────────────
    # Construcción de la UI
    # ──────────────────────────────────────────────

    def _construir_ui(self):
        # Cabecera
        cab = tk.Frame(self, bg=C_FONDO, pady=10)
        cab.pack(fill=tk.X, padx=PAD)
        tk.Label(
            cab, text="🕵️  Esteganografía con Rejilla de Cardano",
            font=("Segoe UI", 16, "bold"),
            bg=C_FONDO, fg=C_ACENTO
        ).pack(side=tk.LEFT)
        tk.Label(
            cab,
            text="Oculta mensajes dentro de textos aparentemente inocentes",
            font=("Segoe UI", 10),
            bg=C_FONDO, fg=C_TEXTO_SUB
        ).pack(side=tk.LEFT, padx=14)

        # Contenedor principal
        main = tk.Frame(self, bg=C_FONDO)
        main.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD))

        # Columna izquierda: editor de rejilla
        self._col_izq = tk.Frame(main, bg=C_PANEL, padx=10, pady=10)
        self._col_izq.pack(side=tk.LEFT, fill=tk.Y)
        self._construir_editor_rejilla(self._col_izq)

        # Columna derecha: operaciones (notebook)
        col_der = tk.Frame(main, bg=C_FONDO)
        col_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self._construir_notebook(col_der)

    def _construir_editor_rejilla(self, parent):
        """Panel izquierdo: editor visual de la rejilla."""
        self._lbl_titulo_rej(parent, "EDITOR DE REJILLA")

        # Selector de tamaño
        f_tam = tk.Frame(parent, bg=C_PANEL)
        f_tam.pack(fill=tk.X, pady=4)
        tk.Label(f_tam, text="Tamaño:", bg=C_PANEL, fg=C_TEXTO,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        for tam in (4, 6, 8):
            tk.Radiobutton(
                f_tam, text=f"{tam}×{tam}", variable=self.n, value=tam,
                command=self._cambiar_tamano,
                bg=C_PANEL, fg=C_TEXTO, selectcolor=C_ACENTO,
                activebackground=C_PANEL, font=("Segoe UI", 10)
            ).pack(side=tk.LEFT, padx=3)

        # Canvas de la rejilla
        self.canvas = tk.Canvas(
            parent, bg=C_FONDO, highlightthickness=0,
            width=TAM_CELDA * 8 + PAD * 2,
            height=TAM_CELDA * 8 + PAD * 2
        )
        self.canvas.pack(pady=6)
        self.canvas.bind("<Button-1>", self._clic_canvas)

        # Validación
        self.lbl_val = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_ADVERTENCIA,
            font=("Segoe UI", 9), wraplength=220, justify=tk.LEFT
        )
        self.lbl_val.pack(fill=tk.X)

        # Capacidad
        self.lbl_cap = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_TEXTO_SUB,
            font=("Segoe UI", 9)
        )
        self.lbl_cap.pack(fill=tk.X, pady=(2, 6))

        # Botones de rejilla
        self._btn(parent, "🎲 Generar rejilla válida", self._generar_rejilla)
        self._btn(parent, "🗑️  Limpiar huecos",        self._limpiar_huecos)
        sep = tk.Frame(parent, bg=C_BORDE, height=1)
        sep.pack(fill=tk.X, pady=6)
        f_gc = tk.Frame(parent, bg=C_PANEL)
        f_gc.pack(fill=tk.X)
        self._btn_s(f_gc, "💾 Guardar", self._guardar, tk.LEFT)
        self._btn_s(f_gc, "📂 Cargar",  self._cargar,  tk.LEFT)

        # Leyenda
        sep2 = tk.Frame(parent, bg=C_BORDE, height=1)
        sep2.pack(fill=tk.X, pady=8)
        leyenda = tk.Frame(parent, bg=C_PANEL)
        leyenda.pack(fill=tk.X)
        self._leyenda(leyenda, C_HUECO, "Hueco (posición secreta)")
        self._leyenda(leyenda, C_ROTACION, "Rotación 90°/180°/270°")
        self._leyenda(leyenda, C_CELDA, "Celda normal (relleno)")

    def _construir_notebook(self, parent):
        """Panel derecho con pestañas Ocultar / Revelar."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TNotebook",
            background=C_FONDO, borderwidth=0
        )
        style.configure(
            "Dark.TNotebook.Tab",
            background=C_PANEL, foreground=C_TEXTO,
            padding=(14, 6), font=("Segoe UI", 10)
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", C_ACENTO)],
            foreground=[("selected", "#ffffff")]
        )

        self.nb = ttk.Notebook(parent, style="Dark.TNotebook")
        self.nb.pack(fill=tk.BOTH, expand=True)

        # Pestaña 1: Ocultar
        tab_ocultar = tk.Frame(self.nb, bg=C_PANEL2, padx=12, pady=12)
        self.nb.add(tab_ocultar, text="🔒  Ocultar mensaje")
        self._construir_tab_ocultar(tab_ocultar)

        # Pestaña 2: Revelar
        tab_revelar = tk.Frame(self.nb, bg=C_PANEL2, padx=12, pady=12)
        self.nb.add(tab_revelar, text="🔓  Revelar mensaje")
        self._construir_tab_revelar(tab_revelar)

        # Pestaña 3: Animación
        tab_anim = tk.Frame(self.nb, bg=C_PANEL2, padx=16, pady=14)
        self.nb.add(tab_anim, text="📽️  Animación")
        self._construir_tab_animacion(tab_anim)

    def _construir_tab_ocultar(self, parent):
        """Pestaña para ocultar un mensaje secreto."""
        # Mensaje secreto
        self._lbl_sec(parent, "MENSAJE SECRETO")
        self.entry_secreto = tk.Text(
            parent, height=2, bg=C_CELDA, fg=C_TEXTO,
            insertbackground=C_TEXTO, font=("Segoe UI", 11),
            relief=tk.FLAT, padx=8, pady=6
        )
        self.entry_secreto.pack(fill=tk.X, pady=(2, 8))

        # Modo de generación
        self._lbl_sec(parent, "TEXTO DE COBERTURA")
        self.modo_cobertura = tk.StringVar(value="auto")
        f_modo = tk.Frame(parent, bg=C_PANEL2)
        f_modo.pack(fill=tk.X, pady=2)
        tk.Radiobutton(
            f_modo, text="🤖 Generar automáticamente",
            variable=self.modo_cobertura, value="auto",
            command=self._toggle_modo_cobertura,
            bg=C_PANEL2, fg=C_TEXTO, selectcolor=C_ACENTO,
            activebackground=C_PANEL2, font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 12))
        tk.Radiobutton(
            f_modo, text="✍️  Escribir manualmente",
            variable=self.modo_cobertura, value="manual",
            command=self._toggle_modo_cobertura,
            bg=C_PANEL2, fg=C_TEXTO, selectcolor=C_ACENTO,
            activebackground=C_PANEL2, font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)

        # Área de texto de cobertura manual
        tk.Label(
            parent,
            text="Escribe aquí el texto de cobertura (solo en modo manual):",
            bg=C_PANEL2, fg=C_TEXTO_SUB, font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(6, 2))
        self.text_cobertura_in = tk.Text(
            parent, height=5, bg=C_CELDA, fg=C_TEXTO,
            insertbackground=C_TEXTO, font=("Segoe UI", 10),
            relief=tk.FLAT, padx=8, pady=6, state=tk.DISABLED
        )
        self.text_cobertura_in.pack(fill=tk.X, pady=(0, 8))

        # Botón ocultar
        self._btn(parent, "🔒  Ocultar mensaje en el texto", self._ocultar)

        # Advertencias
        self.lbl_adv = tk.Label(
            parent, text="", bg=C_PANEL2, fg=C_ADVERTENCIA,
            font=("Segoe UI", 9), wraplength=550, justify=tk.LEFT
        )
        self.lbl_adv.pack(fill=tk.X, pady=4)

        # Resultado resaltado
        self._construir_area_resultado(parent, "ocultar")

    def _construir_tab_revelar(self, parent):
        """Pestaña para revelar un mensaje desde un texto de cobertura."""
        self._lbl_sec(parent, "PEGA AQUÍ EL TEXTO DE COBERTURA")
        tk.Label(
            parent,
            text="Pega el texto que obtuviste al ocultar (con o sin espacios).",
            bg=C_PANEL2, fg=C_TEXTO_SUB, font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(0, 4))

        self.text_cobertura_rev = tk.Text(
            parent, height=6, bg=C_CELDA, fg=C_TEXTO,
            insertbackground=C_TEXTO, font=("Segoe UI", 10),
            relief=tk.FLAT, padx=8, pady=6
        )
        self.text_cobertura_rev.pack(fill=tk.X, pady=(0, 8))

        # Botón revelar
        self._btn(parent, "🔓  Revelar mensaje oculto", self._revelar)

        # Mensaje revelado
        self._lbl_sec(parent, "MENSAJE REVELADO")
        self.lbl_revelado = tk.Label(
            parent, text="", bg=C_PANEL2, fg=C_ACENTO2,
            font=("Courier New", 14, "bold"), wraplength=550, justify=tk.LEFT
        )
        self.lbl_revelado.pack(anchor=tk.W, pady=4)

        # Resultado resaltado
        self._construir_area_resultado(parent, "revelar")

    def _construir_area_resultado(self, parent, modo):
        """Área de texto con resaltado de letras secretas."""
        self._lbl_sec(parent, "VISUALIZACIÓN DEL TEXTO DE COBERTURA")

        controles = tk.Frame(parent, bg=C_PANEL2)
        controles.pack(fill=tk.X, pady=(2, 4))

        if modo == "ocultar":
            tk.Checkbutton(
                controles, text="Mostrar letras secretas resaltadas",
                variable=self.mostrar_resaltado,
                command=self._actualizar_resaltado_ocultar,
                bg=C_PANEL2, fg=C_TEXTO, selectcolor=C_ACENTO,
                activebackground=C_PANEL2, font=("Segoe UI", 10)
            ).pack(side=tk.LEFT)
            self._btn_s(controles, "📋 Copiar texto limpio",
                        self._copiar_texto_limpio, tk.RIGHT)
        else:
            tk.Checkbutton(
                controles, text="Mostrar letras secretas resaltadas",
                variable=self.mostrar_resaltado,
                command=self._actualizar_resaltado_revelar,
                bg=C_PANEL2, fg=C_TEXTO, selectcolor=C_ACENTO,
                activebackground=C_PANEL2, font=("Segoe UI", 10)
            ).pack(side=tk.LEFT)

        # Frame con scrollbar para el texto
        f_text = tk.Frame(parent, bg=C_PANEL2)
        f_text.pack(fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(f_text, bg=C_PANEL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        widget_name = f"text_resultado_{modo}"
        text_widget = tk.Text(
            f_text, height=8,
            bg=C_NORMAL_BG, fg=C_NORMAL_FG,
            insertbackground=C_TEXTO,
            font=("Courier New", 11),
            relief=tk.FLAT, padx=10, pady=8,
            wrap=tk.WORD,
            yscrollcommand=scroll.set,
            state=tk.DISABLED
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=text_widget.yview)

        # Configurar etiquetas de resaltado
        text_widget.tag_configure(
            "secreto",
            background=C_SECRETO_BG,
            foreground=C_SECRETO_FG,
            font=("Courier New", 11, "bold")
        )
        text_widget.tag_configure(
            "normal",
            foreground=C_NORMAL_FG
        )

        setattr(self, widget_name, text_widget)

    # ──────────────────────────────────────────────
    # Helpers de UI
    # ──────────────────────────────────────────────

    def _lbl_titulo_rej(self, parent, texto):
        tk.Label(
            parent, text=texto,
            bg=C_PANEL, fg=C_ACENTO,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 4))
        tk.Frame(parent, bg=C_ACENTO, height=1).pack(fill=tk.X, pady=(0, 6))

    def _lbl_sec(self, parent, texto):
        tk.Label(
            parent, text=texto,
            bg=parent.cget("bg"), fg=C_ACENTO,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor=tk.W, pady=(8, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 4))

    def _btn(self, parent, texto, cmd):
        b = tk.Button(
            parent, text=texto, command=cmd,
            bg=C_BTN, fg=C_TEXTO,
            activebackground=C_BTN_HOVER, activeforeground=C_TEXTO,
            font=("Segoe UI", 10), relief=tk.FLAT,
            padx=10, pady=6, cursor="hand2"
        )
        b.pack(fill=tk.X, pady=2)
        return b

    def _btn_s(self, parent, texto, cmd, side):
        b = tk.Button(
            parent, text=texto, command=cmd,
            bg=C_BTN, fg=C_TEXTO,
            activebackground=C_BTN_HOVER, activeforeground=C_TEXTO,
            font=("Segoe UI", 9), relief=tk.FLAT,
            padx=8, pady=4, cursor="hand2"
        )
        b.pack(side=side, padx=2)
        return b

    def _leyenda(self, parent, color, texto):
        f = tk.Frame(parent, bg=C_PANEL)
        f.pack(anchor=tk.W, pady=2)
        tk.Canvas(f, width=16, height=16, bg=C_PANEL,
                  highlightthickness=0).pack(side=tk.LEFT)
        c = tk.Canvas(f, width=16, height=16, bg=C_PANEL, highlightthickness=0)
        c.pack(side=tk.LEFT)
        c.create_rectangle(1, 1, 15, 15, fill=color, outline="")
        tk.Label(f, text=texto, bg=C_PANEL, fg=C_TEXTO_SUB,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=4)

    # ──────────────────────────────────────────────
    # Dibujo de la rejilla
    # ──────────────────────────────────────────────

    def _dibujar_rejilla(self, celda_activa=None):
        self.canvas.delete("all")
        n = self.n.get()
        tam = TAM_CELDA
        ox = PAD
        oy = PAD

        for fila in range(n):
            for col in range(n):
                x1 = ox + col * tam
                y1 = oy + fila * tam
                x2 = x1 + tam
                y2 = y1 + tam
                celda = (fila, col)

                if celda == celda_activa:
                    fill = C_ACENTO2     # cian brillante = celda activa en animación
                    borde = "#ffffff"
                elif celda in self.huecos:
                    fill = C_HUECO
                    borde = C_HUECO_BORDE
                elif celda in self.huecos_rotados:
                    fill = C_ROTACION
                    borde = C_ROTACION_BORDE
                else:
                    fill = C_CELDA
                    borde = C_CELDA_BORDE

                self.canvas.create_rectangle(
                    x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                    fill=fill, outline=borde, width=2
                )

                # Número de posición lineal
                pos = fila * n + col
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(pos),
                    fill="#64748b" if celda not in self.huecos else "#c4b5fd",
                    font=("Segoe UI", 8)
                )

                # Etiqueta de rotación en celdas fantasma
                if celda in self.huecos_rotados:
                    angulo_label = self._angulo_de_celda_rotada(celda)
                    if angulo_label:
                        self.canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2,
                            text=angulo_label,
                            fill=C_ROTACION_BORDE,
                            font=("Segoe UI", 8, "bold")
                        )

        # Números de fila y columna
        for i in range(n):
            self.canvas.create_text(
                ox + i * tam + tam // 2, oy - 10,
                text=str(i), fill=C_TEXTO_SUB, font=("Segoe UI", 8)
            )
            self.canvas.create_text(
                ox - 10, oy + i * tam + tam // 2,
                text=str(i), fill=C_TEXTO_SUB, font=("Segoe UI", 8)
            )

        # Ajustar tamaño del canvas
        ancho = ox * 2 + n * tam
        alto = oy * 2 + n * tam
        self.canvas.config(width=ancho, height=alto)

    def _clic_canvas(self, event):
        n = self.n.get()
        col = (event.x - PAD) // TAM_CELDA
        fila = (event.y - PAD) // TAM_CELDA
        if 0 <= fila < n and 0 <= col < n:
            celda = (fila, col)
            if celda in self.huecos:
                self.huecos.discard(celda)
            else:
                self.huecos.add(celda)
            self._actualizar_rotaciones_preview()
            self._dibujar_rejilla()
            self._actualizar_info_rejilla()

    def _actualizar_info_rejilla(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if valida:
            self.lbl_val.config(text="✓ Rejilla válida", fg=C_EXITO)
            cap = len(self.huecos)
            self.lbl_cap.config(text=f"Capacidad: {cap} caracteres secretos")
        else:
            self.lbl_val.config(text=f"✗ {msg}", fg=C_PELIGRO)
            self.lbl_cap.config(text="")

    # ──────────────────────────────────────────────
    # Acciones
    # ──────────────────────────────────────────────

    def _cambiar_tamano(self):
        self.huecos.clear()
        self.huecos_rotados.clear()
        self._rotaciones_por_angulo = {}
        self._chars_actuales = []
        self._posiciones_actuales = []
        self._dibujar_rejilla()
        self.lbl_val.config(text="")
        self.lbl_cap.config(text="")

    def _generar_rejilla(self):
        n = self.n.get()
        self.huecos = generar_rejilla_valida(n)
        self._actualizar_rotaciones_preview()
        self._dibujar_rejilla()
        self._actualizar_info_rejilla()

    def _limpiar_huecos(self):
        self.huecos.clear()
        self.huecos_rotados.clear()
        self._rotaciones_por_angulo = {}
        self._chars_actuales = []
        self._posiciones_actuales = []
        self._dibujar_rejilla()
        self.lbl_val.config(text="")
        self.lbl_cap.config(text="")

    def _guardar(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if not valida:
            messagebox.showerror("Rejilla inválida", msg)
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Guardar rejilla"
        )
        if ruta:
            guardar_configuracion(self.huecos, n, ruta)
            messagebox.showinfo("Guardado", f"Rejilla guardada en:\n{ruta}")

    def _cargar(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Cargar rejilla"
        )
        if ruta:
            try:
                huecos, n = cargar_configuracion(ruta)
                self.n.set(n)
                self.huecos = huecos
                self._actualizar_rotaciones_preview()
                self._dibujar_rejilla()
                self._actualizar_info_rejilla()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar:\n{e}")

    def _actualizar_rotaciones_preview(self):
        """
        Calcula y resalta las celdas que ocupan los huecos al rotar
        90°, 180° y 270° para vista previa.
        """
        from logica.steganografia import obtener_todas_rotaciones
        n = self.n.get()
        self.huecos_rotados = set()
        self._rotaciones_por_angulo = {}

        if not self.huecos:
            return

        rotaciones = obtener_todas_rotaciones(self.huecos, n)
        angulos = [90, 180, 270]

        for idx, rot in enumerate(rotaciones[1:]):
            angulo_str = f"{angulos[idx]}°"
            for celda in rot:
                if celda not in self.huecos:
                    self.huecos_rotados.add(celda)
                    if celda not in self._rotaciones_por_angulo:
                        self._rotaciones_por_angulo[celda] = angulo_str

    def _angulo_de_celda_rotada(self, celda):
        """Devuelve el ángulo de rotación que produce esta celda, o None."""
        return self._rotaciones_por_angulo.get(celda)

    def _toggle_modo_cobertura(self):
        es_manual = self.modo_cobertura.get() == "manual"
        estado = tk.NORMAL if es_manual else tk.DISABLED
        bg_color = C_CELDA if es_manual else C_PANEL
        self.text_cobertura_in.config(state=estado, bg=bg_color)

    def _ocultar(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if not valida:
            messagebox.showerror("Rejilla inválida", msg)
            return

        secreto = self.entry_secreto.get("1.0", tk.END).strip()
        if not secreto:
            messagebox.showwarning("Sin mensaje", "Escribe el mensaje secreto.")
            return

        modo = self.modo_cobertura.get()
        texto_manual = None
        if modo == "manual":
            texto_manual = self.text_cobertura_in.get("1.0", tk.END).strip()
            if not texto_manual:
                messagebox.showwarning(
                    "Sin cobertura",
                    "Escribe el texto de cobertura en el campo correspondiente."
                )
                return
            # Limitación 4: avisar si el texto es demasiado corto antes de mezclar
            from logica.steganografia import parrafo_a_chars as _p2c
            chars_disponibles = len(_p2c(texto_manual))
            total_necesario = n * n
            if chars_disponibles < total_necesario:
                faltan = total_necesario - chars_disponibles
                continuar = messagebox.askyesno(
                    "Texto de cobertura corto",
                    f"Tu texto de cobertura tiene {chars_disponibles} letras, "
                    f"pero se necesitan {total_necesario}.\n\n"
                    f"Faltan {faltan} caracteres que se rellenarán automáticamente "
                    f"con sílabas, lo que puede romper la naturalidad del texto.\n\n"
                    f"¿Deseas continuar de todas formas?"
                )
                if not continuar:
                    return

        chars, posiciones, msg_usado, advertencias = ocultar_mensaje(
            secreto, self.huecos, n, texto_manual
        )

        self._chars_ocultar = chars
        self._pos_ocultar = posiciones

        # Mostrar advertencias
        if advertencias:
            self.lbl_adv.config(text="⚠ " + " | ".join(advertencias))
        else:
            self.lbl_adv.config(text=f"✓ Mensaje '{msg_usado}' ocultado correctamente.")

        # Formato del texto con espacios (para lectura natural)
        texto_formateado = texto_a_parrafo(chars, n, palabras=True)

        # Mostrar en el widget de resultado
        self._poblar_texto_resaltado(
            self.text_resultado_ocultar,
            texto_formateado,
            posiciones,
            self.mostrar_resaltado.get()
        )

        # Inicializar animación paso a paso
        self._iniciar_animacion(msg_usado, posiciones, n)

    def _revelar(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if not valida:
            messagebox.showerror("Rejilla inválida", msg)
            return

        texto = self.text_cobertura_rev.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Sin texto", "Pega el texto de cobertura.")
            return

        mensaje, posiciones, chars, error = revelar_mensaje(texto, self.huecos, n)

        if error:
            messagebox.showerror("Error", error)
            return

        self._chars_revelar = chars
        self._pos_revelar = posiciones
        self._texto_original_revelar = texto  # guardar texto original del usuario

        self.lbl_revelado.config(text=f"→  {mensaje}")

        # Fix limitación 3: resaltar sobre el texto original, no reconstruido
        self._poblar_texto_original_resaltado(
            self.text_resultado_revelar,
            texto,
            posiciones,
            n,
            self.mostrar_resaltado.get()
        )

    # ──────────────────────────────────────────────
    # Resaltado de texto
    # ──────────────────────────────────────────────

    def _poblar_texto_resaltado(self, widget, texto_formateado, posiciones_secretas, resaltar):
        """
        Llena el widget Text con el texto formateado,
        resaltando las letras en posiciones secretas si resaltar=True.
        """
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)

        if not resaltar:
            widget.insert(tk.END, texto_formateado)
            widget.config(state=tk.DISABLED)
            return

        # Reconstruir texto char a char, rastreando posición en el array original
        pos_set = set(posiciones_secretas)
        idx_original = 0  # índice en el array de chars sin espacios

        for char in texto_formateado:
            if char == ' ':
                widget.insert(tk.END, ' ')
            else:
                tag = "secreto" if idx_original in pos_set else "normal"
                widget.insert(tk.END, char, tag)
                idx_original += 1

        widget.config(state=tk.DISABLED)

    def _actualizar_resaltado_ocultar(self):
        if not hasattr(self, '_chars_ocultar') or not self._chars_ocultar:
            return
        n = self.n.get()
        texto_formateado = texto_a_parrafo(self._chars_ocultar, n, palabras=True)
        self._poblar_texto_resaltado(
            self.text_resultado_ocultar,
            texto_formateado,
            self._pos_ocultar,
            self.mostrar_resaltado.get()
        )

    def _actualizar_resaltado_revelar(self):
        if not hasattr(self, '_chars_revelar') or not self._chars_revelar:
            return
        n = self.n.get()
        self._poblar_texto_original_resaltado(
            self.text_resultado_revelar,
            self._texto_original_revelar,
            self._pos_revelar,
            n,
            self.mostrar_resaltado.get()
        )

    def _copiar_texto_limpio(self):
        if hasattr(self, '_chars_ocultar') and self._chars_ocultar:
            n = self.n.get()
            texto = texto_a_parrafo(self._chars_ocultar, n, palabras=True)
            self.clipboard_clear()
            self.clipboard_append(texto)
            messagebox.showinfo("Copiado", "Texto de cobertura copiado al portapapeles.")

    # ──────────────────────────────────────────────
    # Fix limitación 3: resaltar sobre texto original del usuario
    # ──────────────────────────────────────────────

    def _poblar_texto_original_resaltado(self, widget, texto_original, posiciones_secretas, n, resaltar):
        """
        Resalta las letras secretas sobre el texto ORIGINAL pegado por el usuario,
        sin reconstruirlo. Rastrea el índice en el array de chars (solo alfa) para
        saber cuándo estamos en una posición secreta.
        """
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)

        if not resaltar or not posiciones_secretas:
            widget.insert(tk.END, texto_original)
            widget.config(state=tk.DISABLED)
            return

        pos_set = set(posiciones_secretas)
        total = n * n
        idx_alpha = 0  # índice en el array de chars sin espacios

        for char in texto_original:
            if char.isalpha():
                if idx_alpha < total and idx_alpha in pos_set:
                    widget.insert(tk.END, char.upper(), "secreto")
                else:
                    widget.insert(tk.END, char.upper(), "normal")
                idx_alpha += 1
                if idx_alpha >= total:
                    # Los caracteres restantes van sin tag
                    break
            else:
                widget.insert(tk.END, char)

        # Si quedó texto después de los n² chars útiles, lo añadimos sin formato
        resto_idx = 0
        conteo_alpha = 0
        for c in texto_original:
            if c.isalpha():
                conteo_alpha += 1
            if conteo_alpha > total:
                widget.insert(tk.END, texto_original[resto_idx:])
                break
            resto_idx += 1

        widget.config(state=tk.DISABLED)

    # ──────────────────────────────────────────────
    # Animación paso a paso (limitación 2)
    # ──────────────────────────────────────────────

    def _construir_tab_animacion(self, parent):
        """Pestaña dedicada a la animación paso a paso del ocultamiento."""
        bg = C_PANEL2

        # ── Caja de estado del paso actual (prominente) ──
        f_info = tk.Frame(parent, bg="#1a2744", bd=0)
        f_info.pack(fill=tk.X, pady=(0, 14))
        tk.Label(
            f_info, text="PASO ACTUAL",
            bg="#1a2744", fg=C_ACENTO,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor=tk.W, padx=12, pady=(8, 0))
        self.lbl_paso_info = tk.Label(
            f_info,
            text="Pulsa  🔒 Ocultar mensaje  para iniciar la animación.",
            bg="#1a2744", fg=C_TEXTO_SUB,
            font=("Segoe UI", 13), wraplength=600, justify=tk.LEFT
        )
        self.lbl_paso_info.pack(anchor=tk.W, padx=12, pady=(2, 10))

        # ── Controles de navegación ──
        f_ctrl = tk.Frame(parent, bg=bg)
        f_ctrl.pack(fill=tk.X, pady=(0, 8))

        self.btn_anim_inicio    = self._btn_s(f_ctrl, "|◀  Inicio",    self._anim_ir_inicio,   tk.LEFT)
        self.btn_anim_anterior  = self._btn_s(f_ctrl, "◀  Anterior",   self._anim_anterior,    tk.LEFT)
        self.btn_anim_auto      = self._btn_s(f_ctrl, "▶  Auto",        self._anim_toggle_auto, tk.LEFT)
        self.btn_anim_siguiente = self._btn_s(f_ctrl, "Siguiente  ▶",  self._anim_siguiente,   tk.LEFT)
        self.btn_anim_fin       = self._btn_s(f_ctrl, "Fin  ▶|",        self._anim_ir_fin,      tk.LEFT)

        # ── Slider de velocidad ──
        f_vel = tk.Frame(parent, bg=bg)
        f_vel.pack(fill=tk.X, pady=(0, 12))
        tk.Label(f_vel, text="Velocidad:", bg=bg, fg=C_TEXTO_SUB,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.slider_vel = tk.Scale(
            f_vel, from_=200, to=2000, orient=tk.HORIZONTAL,
            resolution=100, length=220,
            bg=bg, fg=C_TEXTO, troughcolor=C_BORDE,
            highlightthickness=0, label="", showvalue=False
        )
        self.slider_vel.set(800)
        self.slider_vel.pack(side=tk.LEFT, padx=8)
        tk.Label(f_vel, text="Rápido ←                         → Lento",
                 bg=bg, fg=C_TEXTO_SUB, font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # ── Tabla de posiciones secretas ──
        self._lbl_sec(parent, "TABLA DE POSICIONES SECRETAS")
        f_tabla = tk.Frame(parent, bg=bg)
        f_tabla.pack(fill=tk.BOTH, expand=True)

        scroll_t = tk.Scrollbar(f_tabla, bg=C_PANEL)
        scroll_t.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_tabla_pasos = tk.Text(
            f_tabla,
            bg=C_CELDA, fg=C_TEXTO_SUB,
            font=("Courier New", 11),
            relief=tk.FLAT, padx=12, pady=8,
            state=tk.DISABLED,
            yscrollcommand=scroll_t.set
        )
        self.text_tabla_pasos.pack(fill=tk.BOTH, expand=True)
        scroll_t.config(command=self.text_tabla_pasos.yview)

        self.text_tabla_pasos.tag_configure(
            "activo",
            background=C_ACENTO2, foreground="#0f172a",
            font=("Courier New", 11, "bold")
        )
        self.text_tabla_pasos.tag_configure("hecho", foreground=C_EXITO)
        self.text_tabla_pasos.tag_configure(
            "encabezado", foreground=C_ACENTO, font=("Courier New", 11, "bold")
        )

        # ── Nota de uso ──
        tk.Label(
            parent,
            text="ℹ  El grid de la izquierda resalta en cian la celda activa en cada paso.",
            bg=bg, fg=C_TEXTO_SUB, font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(8, 0))

        self._set_botones_anim(False)

    def _set_botones_anim(self, activo):
        estado = tk.NORMAL if activo else tk.DISABLED
        for b in (self.btn_anim_inicio, self.btn_anim_anterior,
                  self.btn_anim_auto, self.btn_anim_siguiente, self.btn_anim_fin):
            b.config(state=estado)

    def _iniciar_animacion(self, mensaje_usado, posiciones, n):
        """Prepara los datos de animación y muestra el paso 0."""
        # Cancelar auto si estaba corriendo
        if self._job_auto:
            self.after_cancel(self._job_auto)
            self._job_auto = None
        self._auto_corriendo = False
        self.btn_anim_auto.config(text="▶ Auto")

        # Construir lista de pasos
        self._pasos_animacion = []
        for i, pos in enumerate(posiciones):
            letra = mensaje_usado[i] if i < len(mensaje_usado) else "·"
            self._pasos_animacion.append({
                'letra':     letra,
                'pos_lineal': pos,
                'fila':      pos // n,
                'col':       pos % n,
                'num':       i + 1,
            })

        self._paso_actual = -1
        self._celda_activa_anim = None
        self._set_botones_anim(True)
        self._poblar_tabla_pasos()
        self._mostrar_paso_info("Usa los botones para avanzar paso a paso o pulsa  ▶ Auto.")
        self._dibujar_rejilla(celda_activa=None)

        # Saltar automáticamente a la pestaña de animación
        self.nb.select(2)

    def _poblar_tabla_pasos(self):
        """Llena la tabla de pasos (sin resaltado activo aún)."""
        self.text_tabla_pasos.config(state=tk.NORMAL)
        self.text_tabla_pasos.delete("1.0", tk.END)
        encabezado = f"{'Paso':>4}  {'Letra':>5}  {'Fila':>4}  {'Col':>3}  {'Índice':>6}\n"
        sep_tabla  = "─" * 35 + "\n"
        self.text_tabla_pasos.insert(tk.END, encabezado, "encabezado")
        self.text_tabla_pasos.insert(tk.END, sep_tabla)
        for p in self._pasos_animacion:
            linea = f"{p['num']:>4}  {p['letra']:>5}  {p['fila']:>4}  {p['col']:>3}  {p['pos_lineal']:>6}\n"
            self.text_tabla_pasos.insert(tk.END, linea, f"fila_{p['num']}")
        self.text_tabla_pasos.config(state=tk.DISABLED)

    def _mostrar_paso(self, idx):
        """Avanza la animación al paso idx (0-indexed en _pasos_animacion)."""
        if not self._pasos_animacion:
            return
        idx = max(-1, min(idx, len(self._pasos_animacion) - 1))
        self._paso_actual = idx

        if idx == -1:
            self._celda_activa_anim = None
            self._mostrar_paso_info("Inicio — pulsa 'Siguiente' para avanzar.")
            self._dibujar_rejilla(celda_activa=None)
            self._actualizar_tabla_resaltado(-1)
            return

        paso = self._pasos_animacion[idx]
        self._celda_activa_anim = (paso['fila'], paso['col'])
        self._dibujar_rejilla(celda_activa=self._celda_activa_anim)

        total = len(self._pasos_animacion)
        self._mostrar_paso_info(
            f"Paso {paso['num']}/{total}:  letra '{paso['letra']}'  →  "
            f"celda ({paso['fila']}, {paso['col']})  [índice {paso['pos_lineal']}]"
        )
        self._actualizar_tabla_resaltado(idx)

    def _actualizar_tabla_resaltado(self, idx_activo):
        """Resalta la fila activa en la tabla y marca en verde las ya procesadas."""
        self.text_tabla_pasos.config(state=tk.NORMAL)
        for p in self._pasos_animacion:
            tag_fila = f"fila_{p['num']}"
            self.text_tabla_pasos.tag_remove("activo", f"1.0", tk.END)
            self.text_tabla_pasos.tag_remove("hecho",  f"1.0", tk.END)

        # Reconstruir tags por fila (línea 3 en adelante = encabezado + sep + filas)
        for i, p in enumerate(self._pasos_animacion):
            linea_num = i + 3  # 1=encabezado, 2=separador, 3+=datos
            inicio = f"{linea_num}.0"
            fin    = f"{linea_num}.end"
            if i == idx_activo:
                self.text_tabla_pasos.tag_add("activo", inicio, fin)
            elif i < idx_activo:
                self.text_tabla_pasos.tag_add("hecho",  inicio, fin)

        # Hacer scroll a la fila activa
        if idx_activo >= 0:
            linea_scroll = idx_activo + 3
            self.text_tabla_pasos.see(f"{linea_scroll}.0")

        self.text_tabla_pasos.config(state=tk.DISABLED)

    def _mostrar_paso_info(self, texto):
        self.lbl_paso_info.config(text=texto, fg=C_ACENTO2)

    def _anim_siguiente(self):
        self._mostrar_paso(self._paso_actual + 1)

    def _anim_anterior(self):
        self._mostrar_paso(self._paso_actual - 1)

    def _anim_ir_inicio(self):
        if self._auto_corriendo:
            self._anim_toggle_auto()
        self._mostrar_paso(-1)

    def _anim_ir_fin(self):
        if self._auto_corriendo:
            self._anim_toggle_auto()
        self._mostrar_paso(len(self._pasos_animacion) - 1)

    def _anim_toggle_auto(self):
        if self._auto_corriendo:
            # Detener
            if self._job_auto:
                self.after_cancel(self._job_auto)
                self._job_auto = None
            self._auto_corriendo = False
            self.btn_anim_auto.config(text="▶ Auto")
        else:
            # Arrancar desde inicio si ya terminó
            if self._paso_actual >= len(self._pasos_animacion) - 1:
                self._mostrar_paso(-1)
            self._auto_corriendo = True
            self.btn_anim_auto.config(text="⏹ Detener")
            self._tick_auto()

    def _tick_auto(self):
        if not self._auto_corriendo:
            return
        siguiente = self._paso_actual + 1
        if siguiente >= len(self._pasos_animacion):
            self._auto_corriendo = False
            self.btn_anim_auto.config(text="▶ Auto")
            self._mostrar_paso_info(
                f"✓ Animación completa — {len(self._pasos_animacion)} letras ocultadas."
            )
            return
        self._mostrar_paso(siguiente)
        delay = self.slider_vel.get()
        self._job_auto = self.after(delay, self._tick_auto)

