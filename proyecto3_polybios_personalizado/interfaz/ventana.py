# interfaz.py - Interfaz Gráfica del Proyecto 3: Polybios Personalizable
# Cuadrícula interactiva con drag & drop, cifrado/descifrado animado paso a paso.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import copy

from logica.polybios import (
    PRESETS, clonar_grid, construir_mapa,
    validar_grid, aleatorizar_grid,
    cifrar, descifrar,
    guardar_grid, cargar_grid,
    grid_a_texto,
)

# ──────────────────────────────────────────────
# Paleta de colores
# ──────────────────────────────────────────────
C_FONDO       = "#0f172a"
C_PANEL       = "#1e293b"
C_PANEL2      = "#162032"
C_BORDE       = "#334155"
C_ACENTO      = "#8b5cf6"
C_ACENTO2     = "#22d3ee"
C_EXITO       = "#4ade80"
C_PELIGRO     = "#f87171"
C_ADVERTENCIA = "#fbbf24"
C_TEXTO       = "#e2e8f0"
C_TEXTO_SUB   = "#94a3b8"

C_CELDA_BG    = "#1e293b"
C_CELDA_BRD   = "#475569"
C_CELDA_FUSED = "#1a3a2a"    # fondo de celda fusionada (IJ, NÑ)
C_CELDA_FUSED_BRD = "#22c55e"
C_DRAG_SRC    = "#7c3aed"    # celda origen del drag
C_DRAG_TGT    = "#0891b2"    # celda destino del drag
C_HIGHLIGHT   = "#fbbf24"    # celda resaltada durante animación
C_HIGHLIGHT_BRD = "#fde68a"

C_BTN         = "#3730a3"
C_BTN_HOVER   = "#4338ca"

TAM_CELDA     = 62
PAD           = 14


class AplicacionPolybios(tk.Tk):
    """Ventana principal del personalizador de cuadrícula Polybios."""

    def __init__(self):
        super().__init__()
        self.title("Polybios Personalizable – Proyecto 3")
        self.configure(bg=C_FONDO)
        self.minsize(1100, 700)
        self.resizable(True, True)

        # Estado de la aplicación
        self._preset_actual = '5x5_IJ'
        self._grid = clonar_grid(PRESETS['5x5_IJ']['grid'])
        self._n    = len(self._grid)

        # Estado del drag & drop
        self._drag_src    = None   # (fila, col) origen
        self._drag_tgt    = None   # (fila, col) destino tentativo
        self._drag_ghost  = None   # id del texto flotante en el canvas
        self._drag_orig_x = 0
        self._drag_orig_y = 0

        # Estado de la animación
        self._pasos_anim    = []
        self._paso_idx      = 0
        self._animando      = False
        self._velocidad     = tk.IntVar(value=700)
        self._celda_activa  = None   # (fila, col) resaltada actualmente

        self._construir_ui()
        self._dibujar_grid()

    # ──────────────────────────────────────────────
    # Construcción de la UI
    # ──────────────────────────────────────────────

    def _construir_ui(self):
        # Cabecera
        cab = tk.Frame(self, bg=C_FONDO, pady=10)
        cab.pack(fill=tk.X, padx=PAD)
        tk.Label(
            cab, text="📐  Personalizador de Cuadrícula Polybios",
            font=("Segoe UI", 15, "bold"),
            bg=C_FONDO, fg=C_ACENTO
        ).pack(side=tk.LEFT)
        tk.Label(
            cab, text="Cifra letras como coordenadas (fila, columna)",
            font=("Segoe UI", 10),
            bg=C_FONDO, fg=C_TEXTO_SUB
        ).pack(side=tk.LEFT, padx=14)

        # Contenedor principal
        main = tk.Frame(self, bg=C_FONDO)
        main.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD))

        # Columna izquierda: editor de cuadrícula
        izq = tk.Frame(main, bg=C_PANEL, padx=12, pady=12)
        izq.pack(side=tk.LEFT, fill=tk.Y)
        self._construir_panel_grid(izq)

        # Columna derecha: cifrado / descifrado
        der = tk.Frame(main, bg=C_FONDO)
        der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self._construir_panel_operaciones(der)

    # ── Panel izquierdo: editor ──────────────────

    def _construir_panel_grid(self, parent):
        self._lbl_sec(parent, "PRESET DE CUADRÍCULA", C_PANEL)

        # Selector de preset
        self._var_preset = tk.StringVar(value='5x5_IJ')
        for key, datos in PRESETS.items():
            tk.Radiobutton(
                parent, text=datos['nombre'],
                variable=self._var_preset, value=key,
                command=self._cargar_preset,
                bg=C_PANEL, fg=C_TEXTO, selectcolor=C_ACENTO,
                activebackground=C_PANEL, font=("Segoe UI", 9)
            ).pack(anchor=tk.W, pady=1)

        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=8)

        self._lbl_sec(parent, "EDITOR DE CUADRÍCULA (arrastrar para intercambiar)", C_PANEL)

        # Canvas principal de la cuadrícula
        self.canvas = tk.Canvas(
            parent, bg=C_FONDO, highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack()

        # Eventos de drag & drop
        self.canvas.bind("<ButtonPress-1>",   self._drag_inicio)
        self.canvas.bind("<B1-Motion>",        self._drag_mover)
        self.canvas.bind("<ButtonRelease-1>",  self._drag_fin)

        # Validación
        self.lbl_val = tk.Label(
            parent, text="", bg=C_PANEL, fg=C_ADVERTENCIA,
            font=("Segoe UI", 9), wraplength=300, justify=tk.LEFT
        )
        self.lbl_val.pack(fill=tk.X, pady=4)

        # Botones de gestión
        f_botones = tk.Frame(parent, bg=C_PANEL)
        f_botones.pack(fill=tk.X, pady=4)
        self._btn_s(f_botones, "🔤 Estándar",    self._cargar_preset,     tk.LEFT)
        self._btn_s(f_botones, "🎲 Aleatorizar", self._aleatorizar,       tk.LEFT)

        f_gc = tk.Frame(parent, bg=C_PANEL)
        f_gc.pack(fill=tk.X, pady=2)
        self._btn_s(f_gc, "💾 Guardar", self._guardar, tk.LEFT)
        self._btn_s(f_gc, "📂 Cargar",  self._cargar,  tk.LEFT)

        # Leyenda
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=8)
        self._leyenda(parent, C_CELDA_BG,    C_CELDA_BRD,  "Celda simple")
        self._leyenda(parent, C_CELDA_FUSED, C_CELDA_FUSED_BRD, "Celda fusionada (IJ/NÑ)")
        self._leyenda(parent, C_HIGHLIGHT,   C_HIGHLIGHT_BRD,   "Celda activa (animación)")

    # ── Panel derecho: operaciones ───────────────

    def _construir_panel_operaciones(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("P3.TNotebook",     background=C_FONDO, borderwidth=0)
        style.configure("P3.TNotebook.Tab", background=C_PANEL,  foreground=C_TEXTO,
                        padding=(14, 6), font=("Segoe UI", 10))
        style.map("P3.TNotebook.Tab",
                  background=[("selected", C_ACENTO)],
                  foreground=[("selected", "#ffffff")])

        nb = ttk.Notebook(parent, style="P3.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True)

        tab_c = tk.Frame(nb, bg=C_PANEL2, padx=12, pady=12)
        nb.add(tab_c, text="🔒  Cifrar")
        self._construir_tab_cifrar(tab_c)

        tab_d = tk.Frame(nb, bg=C_PANEL2, padx=12, pady=12)
        nb.add(tab_d, text="🔓  Descifrar")
        self._construir_tab_descifrar(tab_d)

    def _construir_tab_cifrar(self, parent):
        # Texto plano
        self._lbl_sec(parent, "TEXTO PLANO", C_PANEL2)
        self.entry_plano = tk.Text(
            parent, height=3, bg=C_CELDA_BG, fg=C_TEXTO,
            insertbackground=C_TEXTO, font=("Segoe UI", 11),
            relief=tk.FLAT, padx=8, pady=6
        )
        self.entry_plano.pack(fill=tk.X, pady=(2, 8))

        f_btn = tk.Frame(parent, bg=C_PANEL2)
        f_btn.pack(fill=tk.X, pady=4)
        self._btn_s(f_btn, "🔒 Cifrar",            self._cifrar,           tk.LEFT)
        self._btn_s(f_btn, "▶ Paso a paso",         self._paso_siguiente_c, tk.LEFT)
        self._btn_s(f_btn, "▶▶ Animar todo",        self._animar_cifrado,   tk.LEFT)
        self._btn_s(f_btn, "⏮ Reiniciar",           self._reset_anim_c,     tk.LEFT)

        # Velocidad
        f_vel = tk.Frame(parent, bg=C_PANEL2)
        f_vel.pack(fill=tk.X, pady=2)
        tk.Label(f_vel, text="Velocidad:", bg=C_PANEL2, fg=C_TEXTO_SUB,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Scale(f_vel, from_=200, to=2000, orient=tk.HORIZONTAL,
                 variable=self._velocidad, bg=C_PANEL2, fg=C_TEXTO,
                 highlightthickness=0, troughcolor=C_CELDA_BG,
                 length=160).pack(side=tk.LEFT)

        # Resultado
        self._lbl_sec(parent, "RESULTADO CIFRADO", C_PANEL2)
        self.lbl_cifrado = tk.Label(
            parent, text="", bg=C_PANEL2, fg=C_ACENTO2,
            font=("Courier New", 14, "bold"), wraplength=560, justify=tk.LEFT
        )
        self.lbl_cifrado.pack(anchor=tk.W, pady=4)

        # Tabla de pasos
        self._lbl_sec(parent, "TABLA DE PASOS", C_PANEL2)
        self._construir_tabla(parent, "cifrar")

        # Omitidos
        self.lbl_omitidos_c = tk.Label(
            parent, text="", bg=C_PANEL2, fg=C_ADVERTENCIA,
            font=("Segoe UI", 9), wraplength=560
        )
        self.lbl_omitidos_c.pack(anchor=tk.W)

    def _construir_tab_descifrar(self, parent):
        # Texto cifrado
        self._lbl_sec(parent, "COORDENADAS CIFRADAS", C_PANEL2)
        tk.Label(
            parent,
            text='Ingresa pares de coordenadas separados por espacios  (ej. "23 35 31 11")',
            bg=C_PANEL2, fg=C_TEXTO_SUB, font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(0, 4))
        self.entry_cifrado = tk.Text(
            parent, height=3, bg=C_CELDA_BG, fg=C_TEXTO,
            insertbackground=C_TEXTO, font=("Courier New", 11),
            relief=tk.FLAT, padx=8, pady=6
        )
        self.entry_cifrado.pack(fill=tk.X, pady=(2, 8))

        f_btn = tk.Frame(parent, bg=C_PANEL2)
        f_btn.pack(fill=tk.X, pady=4)
        self._btn_s(f_btn, "🔓 Descifrar",          self._descifrar,        tk.LEFT)
        self._btn_s(f_btn, "▶ Paso a paso",          self._paso_siguiente_d, tk.LEFT)
        self._btn_s(f_btn, "▶▶ Animar todo",         self._animar_descifrado,tk.LEFT)
        self._btn_s(f_btn, "⏮ Reiniciar",            self._reset_anim_d,     tk.LEFT)

        f_vel = tk.Frame(parent, bg=C_PANEL2)
        f_vel.pack(fill=tk.X, pady=2)
        tk.Label(f_vel, text="Velocidad:", bg=C_PANEL2, fg=C_TEXTO_SUB,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Scale(f_vel, from_=200, to=2000, orient=tk.HORIZONTAL,
                 variable=self._velocidad, bg=C_PANEL2, fg=C_TEXTO,
                 highlightthickness=0, troughcolor=C_CELDA_BG,
                 length=160).pack(side=tk.LEFT)

        # Resultado
        self._lbl_sec(parent, "TEXTO DESCIFRADO", C_PANEL2)
        self.lbl_descifrado = tk.Label(
            parent, text="", bg=C_PANEL2, fg=C_EXITO,
            font=("Courier New", 14, "bold"), wraplength=560, justify=tk.LEFT
        )
        self.lbl_descifrado.pack(anchor=tk.W, pady=4)

        # Tabla de pasos
        self._lbl_sec(parent, "TABLA DE PASOS", C_PANEL2)
        self._construir_tabla(parent, "descifrar")

        self.lbl_errores_d = tk.Label(
            parent, text="", bg=C_PANEL2, fg=C_PELIGRO,
            font=("Segoe UI", 9), wraplength=560
        )
        self.lbl_errores_d.pack(anchor=tk.W)

    def _construir_tabla(self, parent, modo):
        """Tabla scrollable con los pasos del cifrado o descifrado."""
        cols_c = ("Letra", "Celda",    "Fila", "Col", "Coordenadas")
        cols_d = ("Coord", "Fila",     "Col",  "Celda","Letra")
        cols   = cols_c if modo == "cifrar" else cols_d

        frame = tk.Frame(parent, bg=C_PANEL2)
        frame.pack(fill=tk.BOTH, expand=True, pady=4)

        style = ttk.Style()
        style.configure(
            "P3.Treeview",
            background=C_PANEL, foreground=C_TEXTO,
            fieldbackground=C_PANEL, rowheight=24,
            font=("Courier New", 10)
        )
        style.configure(
            "P3.Treeview.Heading",
            background=C_ACENTO, foreground="#ffffff",
            font=("Segoe UI", 9, "bold")
        )
        style.map("P3.Treeview", background=[("selected", C_DRAG_TGT)])

        scroll = tk.Scrollbar(frame, bg=C_PANEL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            style="P3.Treeview", height=7,
            yscrollcommand=scroll.set
        )
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=90, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=tree.yview)

        if modo == "cifrar":
            self.tabla_cifrar = tree
        else:
            self.tabla_descifrar = tree

    # ──────────────────────────────────────────────
    # Helpers de UI
    # ──────────────────────────────────────────────

    def _lbl_sec(self, parent, texto, bg):
        tk.Label(parent, text=texto, bg=bg, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(8, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 4))

    def _btn_s(self, parent, texto, cmd, side):
        b = tk.Button(parent, text=texto, command=cmd,
                      bg=C_BTN, fg=C_TEXTO,
                      activebackground=C_BTN_HOVER, activeforeground=C_TEXTO,
                      font=("Segoe UI", 9), relief=tk.FLAT,
                      padx=8, pady=4, cursor="hand2")
        b.pack(side=side, padx=2, pady=2)
        return b

    def _leyenda(self, parent, bg, borde, texto):
        f = tk.Frame(parent, bg=C_PANEL)
        f.pack(anchor=tk.W, pady=2)
        c = tk.Canvas(f, width=18, height=18, bg=C_PANEL, highlightthickness=0)
        c.pack(side=tk.LEFT)
        c.create_rectangle(2, 2, 16, 16, fill=bg, outline=borde, width=2)
        tk.Label(f, text=texto, bg=C_PANEL, fg=C_TEXTO_SUB,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=6)

    # ──────────────────────────────────────────────
    # Dibujo de la cuadrícula
    # ──────────────────────────────────────────────

    def _celda_xy(self, fila, col):
        """Devuelve (x1, y1, x2, y2) de la celda en el canvas."""
        ox = PAD + 20   # offset para etiquetas de columna
        oy = PAD + 20   # offset para etiquetas de fila
        x1 = ox + col * TAM_CELDA
        y1 = oy + fila * TAM_CELDA
        return x1, y1, x1 + TAM_CELDA, y1 + TAM_CELDA

    def _xy_a_celda(self, x, y):
        """Convierte coordenadas de canvas a (fila, col), o None si fuera de rango."""
        ox = PAD + 20
        oy = PAD + 20
        col  = (x - ox) // TAM_CELDA
        fila = (y - oy) // TAM_CELDA
        n = self._n
        if 0 <= fila < n and 0 <= col < n:
            return (int(fila), int(col))
        return None

    def _dibujar_grid(self, resaltar=None):
        """
        Redibuja la cuadrícula completa.
        resaltar: (fila, col) de la celda a destacar en amarillo.
        """
        self.canvas.delete("all")
        n  = self._n
        ox = PAD + 20
        oy = PAD + 20

        # Etiquetas de columna
        for j in range(n):
            cx = ox + j * TAM_CELDA + TAM_CELDA // 2
            self.canvas.create_text(
                cx, oy - 10,
                text=str(j + 1),
                fill=C_TEXTO_SUB, font=("Segoe UI", 10, "bold")
            )

        # Etiquetas de fila
        for i in range(n):
            cy = oy + i * TAM_CELDA + TAM_CELDA // 2
            self.canvas.create_text(
                ox - 10, cy,
                text=str(i + 1),
                fill=C_TEXTO_SUB, font=("Segoe UI", 10, "bold")
            )

        # Celdas
        for i in range(n):
            for j in range(n):
                x1, y1, x2, y2 = self._celda_xy(i, j)
                celda = self._grid[i][j]
                fusionada = len(celda) > 1

                # Color según estado
                if resaltar == (i, j):
                    fill   = C_HIGHLIGHT
                    borde  = C_HIGHLIGHT_BRD
                    grosor = 3
                elif (i, j) == self._drag_src:
                    fill   = C_DRAG_SRC
                    borde  = "#a78bfa"
                    grosor = 2
                elif (i, j) == self._drag_tgt:
                    fill   = C_DRAG_TGT
                    borde  = "#67e8f9"
                    grosor = 2
                elif fusionada:
                    fill   = C_CELDA_FUSED
                    borde  = C_CELDA_FUSED_BRD
                    grosor = 2
                else:
                    fill   = C_CELDA_BG
                    borde  = C_CELDA_BRD
                    grosor = 1

                self.canvas.create_rectangle(
                    x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                    fill=fill, outline=borde, width=grosor,
                    tags=f"celda_{i}_{j}"
                )

                # Texto de la celda
                color_txt = "#ffffff"
                if resaltar == (i, j):
                    color_txt = "#0f172a"
                elif fusionada:
                    color_txt = "#86efac"

                fontsize = 15 if len(celda) == 1 else 11
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=celda,
                    fill=color_txt,
                    font=("Segoe UI", fontsize, "bold"),
                    tags=f"txt_{i}_{j}"
                )

        # Ajustar tamaño del canvas
        ancho = ox * 2 + n * TAM_CELDA
        alto  = oy * 2 + n * TAM_CELDA
        self.canvas.config(width=ancho, height=alto)

    # ──────────────────────────────────────────────
    # Drag & Drop
    # ──────────────────────────────────────────────

    def _drag_inicio(self, event):
        celda = self._xy_a_celda(event.x, event.y)
        if celda is None:
            return
        self._drag_src   = celda
        self._drag_tgt   = None
        self._drag_orig_x = event.x
        self._drag_orig_y = event.y

        # Crear texto flotante que sigue al mouse
        x1, y1, x2, y2 = self._celda_xy(*celda)
        self._drag_ghost = self.canvas.create_text(
            event.x, event.y,
            text=self._grid[celda[0]][celda[1]],
            fill=C_HIGHLIGHT,
            font=("Segoe UI", 16, "bold"),
            tags="ghost"
        )
        self._dibujar_grid()
        # Subir el ghost al frente
        self.canvas.tag_raise("ghost")

    def _drag_mover(self, event):
        if self._drag_ghost is None:
            return
        # Mover el texto flotante
        self.canvas.coords(self._drag_ghost, event.x, event.y)

        # Determinar celda destino tentativa
        nuevo_tgt = self._xy_a_celda(event.x, event.y)
        if nuevo_tgt != self._drag_src:
            self._drag_tgt = nuevo_tgt
        else:
            self._drag_tgt = None

        self._dibujar_grid()
        self.canvas.tag_raise("ghost")

    def _drag_fin(self, event):
        if self._drag_ghost is not None:
            self.canvas.delete("ghost")
            self._drag_ghost = None

        src = self._drag_src
        tgt = self._drag_tgt

        if src and tgt and src != tgt:
            # Intercambiar contenido de las dos celdas
            si, sj = src
            ti, tj = tgt
            self._grid[si][sj], self._grid[ti][tj] = (
                self._grid[ti][tj],
                self._grid[si][sj],
            )
            self._validar_y_actualizar()

        self._drag_src = None
        self._drag_tgt = None
        self._dibujar_grid()

    # ──────────────────────────────────────────────
    # Acciones de configuración
    # ──────────────────────────────────────────────

    def _cargar_preset(self):
        key = self._var_preset.get()
        self._grid          = clonar_grid(PRESETS[key]['grid'])
        self._n             = len(self._grid)
        self._preset_actual = key
        self._pasos_anim    = []
        self._paso_idx      = 0
        self._celda_activa  = None
        self._dibujar_grid()
        self._validar_y_actualizar()

    def _aleatorizar(self):
        self._grid = aleatorizar_grid(self._grid)
        self._dibujar_grid()
        self._validar_y_actualizar()

    def _validar_y_actualizar(self):
        valida, msg = validar_grid(self._grid)
        if valida:
            self.lbl_val.config(text="✓ Cuadrícula válida", fg=C_EXITO)
        else:
            self.lbl_val.config(text=f"✗ {msg}", fg=C_PELIGRO)

    def _guardar(self):
        valida, msg = validar_grid(self._grid)
        if not valida:
            messagebox.showerror("Cuadrícula inválida", msg)
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Guardar cuadrícula"
        )
        if ruta:
            guardar_grid(self._grid, ruta)
            messagebox.showinfo("Guardado", f"Cuadrícula guardada en:\n{ruta}")

    def _cargar(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Cargar cuadrícula"
        )
        if ruta:
            try:
                grid, n = cargar_grid(ruta)
                self._grid = grid
                self._n    = n
                self._dibujar_grid()
                self._validar_y_actualizar()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar:\n{e}")

    # ──────────────────────────────────────────────
    # Cifrado
    # ──────────────────────────────────────────────

    def _cifrar(self):
        valida, msg = validar_grid(self._grid)
        if not valida:
            messagebox.showerror("Cuadrícula inválida", msg)
            return
        texto = self.entry_plano.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Sin texto", "Ingresa el texto a cifrar.")
            return

        cifrado, pasos, omitidos = cifrar(texto, self._grid)
        self._pasos_anim_c = pasos
        self._paso_idx_c   = 0
        self._animando_c   = False

        self.lbl_cifrado.config(text=cifrado)

        if omitidos:
            self.lbl_omitidos_c.config(
                text=f"⚠ Caracteres omitidos (no están en la cuadrícula): "
                     f"{''.join(set(omitidos))}"
            )
        else:
            self.lbl_omitidos_c.config(text="")

        # Poblar tabla completa
        self._poblar_tabla_cifrar(pasos)

    def _poblar_tabla_cifrar(self, pasos):
        """Llena la tabla de pasos del cifrado."""
        for item in self.tabla_cifrar.get_children():
            self.tabla_cifrar.delete(item)
        for paso in pasos:
            self.tabla_cifrar.insert("", tk.END, values=(
                paso['letra'],
                paso['celda'],
                paso['fila'] + 1,
                paso['col']  + 1,
                paso['coord'],
            ))

    def _paso_siguiente_c(self):
        if not hasattr(self, '_pasos_anim_c') or not self._pasos_anim_c:
            messagebox.showinfo("Sin pasos", "Cifra un texto primero.")
            return
        if self._paso_idx_c >= len(self._pasos_anim_c):
            self._paso_idx_c = 0
        self._mostrar_paso_cifrar(self._paso_idx_c)
        self._paso_idx_c += 1

    def _mostrar_paso_cifrar(self, idx):
        paso = self._pasos_anim_c[idx]
        self._dibujar_grid(resaltar=(paso['fila'], paso['col']))
        # Resaltar fila en tabla
        children = self.tabla_cifrar.get_children()
        if idx < len(children):
            self.tabla_cifrar.selection_set(children[idx])
            self.tabla_cifrar.see(children[idx])

    def _reset_anim_c(self):
        self._paso_idx_c  = 0
        self._animando_c  = False
        self._dibujar_grid()

    def _animar_cifrado(self):
        if not hasattr(self, '_pasos_anim_c') or not self._pasos_anim_c:
            messagebox.showinfo("Sin pasos", "Cifra un texto primero.")
            return
        if getattr(self, '_animando_c', False):
            return
        self._animando_c  = True
        self._paso_idx_c  = 0
        self._tick_anim_c()

    def _tick_anim_c(self):
        if not self._animando_c:
            return
        if self._paso_idx_c >= len(self._pasos_anim_c):
            self._animando_c = False
            self._dibujar_grid()
            return
        self._mostrar_paso_cifrar(self._paso_idx_c)
        self._paso_idx_c += 1
        self.after(self._velocidad.get(), self._tick_anim_c)

    # ──────────────────────────────────────────────
    # Descifrado
    # ──────────────────────────────────────────────

    def _descifrar(self):
        valida, msg = validar_grid(self._grid)
        if not valida:
            messagebox.showerror("Cuadrícula inválida", msg)
            return
        texto_c = self.entry_cifrado.get("1.0", tk.END).strip()
        if not texto_c:
            messagebox.showwarning("Sin texto", "Ingresa las coordenadas a descifrar.")
            return

        descifrado, pasos, errores = descifrar(texto_c, self._grid)
        self._pasos_anim_d = pasos
        self._paso_idx_d   = 0
        self._animando_d   = False

        self.lbl_descifrado.config(text=descifrado)

        if errores:
            self.lbl_errores_d.config(
                text=f"⚠ Tokens no reconocidos: {', '.join(errores)}"
            )
        else:
            self.lbl_errores_d.config(text="")

        # Poblar tabla completa
        self._poblar_tabla_descifrar(pasos)

    def _poblar_tabla_descifrar(self, pasos):
        for item in self.tabla_descifrar.get_children():
            self.tabla_descifrar.delete(item)
        for paso in pasos:
            self.tabla_descifrar.insert("", tk.END, values=(
                paso['coord'],
                paso['fila'] + 1,
                paso['col']  + 1,
                paso['celda'],
                paso['letra'],
            ))

    def _paso_siguiente_d(self):
        if not hasattr(self, '_pasos_anim_d') or not self._pasos_anim_d:
            messagebox.showinfo("Sin pasos", "Descifra un texto primero.")
            return
        if self._paso_idx_d >= len(self._pasos_anim_d):
            self._paso_idx_d = 0
        self._mostrar_paso_descifrar(self._paso_idx_d)
        self._paso_idx_d += 1

    def _mostrar_paso_descifrar(self, idx):
        paso = self._pasos_anim_d[idx]
        self._dibujar_grid(resaltar=(paso['fila'], paso['col']))
        children = self.tabla_descifrar.get_children()
        if idx < len(children):
            self.tabla_descifrar.selection_set(children[idx])
            self.tabla_descifrar.see(children[idx])

    def _reset_anim_d(self):
        self._paso_idx_d  = 0
        self._animando_d  = False
        self._dibujar_grid()

    def _animar_descifrado(self):
        if not hasattr(self, '_pasos_anim_d') or not self._pasos_anim_d:
            messagebox.showinfo("Sin pasos", "Descifra un texto primero.")
            return
        if getattr(self, '_animando_d', False):
            return
        self._animando_d = True
        self._paso_idx_d = 0
        self._tick_anim_d()

    def _tick_anim_d(self):
        if not self._animando_d:
            return
        if self._paso_idx_d >= len(self._pasos_anim_d):
            self._animando_d = False
            self._dibujar_grid()
            return
        self._mostrar_paso_descifrar(self._paso_idx_d)
        self._paso_idx_d += 1
        self.after(self._velocidad.get(), self._tick_anim_d)

