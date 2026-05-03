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
        self.mostrar_resaltado = tk.BooleanVar(value=True)
        self._chars_actuales = []       # lista de n² chars del resultado
        self._posiciones_actuales = []  # posiciones secretas actuales

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

        nb = ttk.Notebook(parent, style="Dark.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True)

        # Pestaña 1: Ocultar
        tab_ocultar = tk.Frame(nb, bg=C_PANEL2, padx=12, pady=12)
        nb.add(tab_ocultar, text="🔒  Ocultar mensaje")
        self._construir_tab_ocultar(tab_ocultar)

        # Pestaña 2: Revelar
        tab_revelar = tk.Frame(nb, bg=C_PANEL2, padx=12, pady=12)
        nb.add(tab_revelar, text="🔓  Revelar mensaje")
        self._construir_tab_revelar(tab_revelar)

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

    def _dibujar_rejilla(self):
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

                if celda in self.huecos:
                    fill = C_HUECO
                    borde = C_HUECO_BORDE
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
        self._chars_actuales = []
        self._posiciones_actuales = []
        self._dibujar_rejilla()
        self.lbl_val.config(text="")
        self.lbl_cap.config(text="")

    def _generar_rejilla(self):
        n = self.n.get()
        self.huecos = generar_rejilla_valida(n)
        self._dibujar_rejilla()
        self._actualizar_info_rejilla()

    def _limpiar_huecos(self):
        self.huecos.clear()
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
                self._dibujar_rejilla()
                self._actualizar_info_rejilla()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar:\n{e}")

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

        self.lbl_revelado.config(text=f"→  {mensaje}")

        texto_formateado = texto_a_parrafo(chars, n, palabras=True)
        self._poblar_texto_resaltado(
            self.text_resultado_revelar,
            texto_formateado,
            posiciones,
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
        texto_formateado = texto_a_parrafo(self._chars_revelar, n, palabras=True)
        self._poblar_texto_resaltado(
            self.text_resultado_revelar,
            texto_formateado,
            self._pos_revelar,
            self.mostrar_resaltado.get()
        )

    def _copiar_texto_limpio(self):
        if hasattr(self, '_chars_ocultar') and self._chars_ocultar:
            n = self.n.get()
            texto = texto_a_parrafo(self._chars_ocultar, n, palabras=True)
            self.clipboard_clear()
            self.clipboard_append(texto)
            messagebox.showinfo("Copiado", "Texto de cobertura copiado al portapapeles.")

