# interfaz.py - Interfaz Gráfica del Simulador de Rejilla de Cardano
# Usa Tkinter + Canvas para la visualización y animaciones

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import time

from logica.rejilla import (
    validar_rejilla,
    cifrar,
    descifrar,
    guardar_rejilla,
    cargar_rejilla,
    generar_rejilla_ejemplo,
    obtener_todas_rotaciones,
)

# ──────────────────────────────────────────────
# Constantes de diseño
# ──────────────────────────────────────────────
COLOR_FONDO        = "#1e1e2e"
COLOR_PANEL        = "#2a2a3e"
COLOR_ACENTO       = "#7c3aed"
COLOR_ACENTO2      = "#06b6d4"
COLOR_TEXTO        = "#e2e8f0"
COLOR_CELDA        = "#3b3b52"
COLOR_CELDA_BORDE  = "#555570"
COLOR_HUECO        = "#7c3aed"
COLOR_HUECO_BORDE  = "#a78bfa"
COLOR_ACTIVO       = "#06b6d4"
COLOR_ACTIVO_BORDE = "#67e8f9"
COLOR_ROTACION     = "#0f3a2e"   # fondo oscuro-verde para posiciones rotadas
COLOR_ROTACION_BORDE = "#10b981" # borde verde para posiciones rotadas
COLOR_LETRA        = "#ffffff"
COLOR_BOTON        = "#4c1d95"
COLOR_BOTON_HOVER  = "#5b21b6"
TAMANIO_CELDA      = 60
PADDING_CANVAS     = 20


class AplicacionRejilla(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title("Rejilla de Cardano - Proyecto 1")
        self.configure(bg=COLOR_FONDO)
        self.resizable(True, True)
        self.minsize(900, 700)

        # Estado de la aplicación
        self.n = tk.IntVar(value=4)          # tamaño de la rejilla
        self.huecos = set()                  # conjunto de celdas hueco (0°)
        self.huecos_rotados = set()          # posiciones de huecos en 90°/180°/270°
        self._rotaciones_por_angulo = {}     # {celda: "90°"/"180°"/"270°"}
        self.modo = tk.StringVar(value="editor")  # editor / cifrar / descifrar
        self.pasos_animacion = []            # pasos del cifrado/descifrado
        self.paso_actual = 0
        self.animando = False
        self.velocidad = tk.IntVar(value=800)  # ms entre frames

        # Matriz del cifrado (para descifrar)
        self.matriz_cifrada = None

        self._construir_ui()
        self._dibujar_rejilla()

    # ──────────────────────────────────────────────
    # Construcción de la UI
    # ──────────────────────────────────────────────

    def _construir_ui(self):
        """Construye todos los paneles de la interfaz."""
        # Marco superior: controles
        marco_top = tk.Frame(self, bg=COLOR_FONDO, pady=8)
        marco_top.pack(fill=tk.X, padx=16)

        tk.Label(
            marco_top, text="🔐 Simulador de Rejilla de Cardano",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_FONDO, fg=COLOR_ACENTO
        ).pack(side=tk.LEFT)

        # Marco principal: canvas + panel lateral
        marco_main = tk.Frame(self, bg=COLOR_FONDO)
        marco_main.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Canvas para la rejilla
        self.frame_canvas = tk.Frame(marco_main, bg=COLOR_FONDO)
        self.frame_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.frame_canvas,
            bg=COLOR_FONDO,
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self._clic_canvas)

        # Panel lateral con scroll
        # Contenedor externo de ancho fijo
        panel_outer = tk.Frame(marco_main, bg=COLOR_PANEL, width=296)
        panel_outer.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0))
        panel_outer.pack_propagate(False)

        # Scrollbar vertical
        scrollbar = tk.Scrollbar(panel_outer, orient=tk.VERTICAL, bg=COLOR_PANEL,
                                 troughcolor=COLOR_CELDA, activebackground=COLOR_ACENTO)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas interno que permite scroll
        self._panel_canvas = tk.Canvas(
            panel_outer, bg=COLOR_PANEL,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self._panel_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._panel_canvas.yview)

        # Frame real donde van los widgets
        self.panel = tk.Frame(self._panel_canvas, bg=COLOR_PANEL, padx=12, pady=12)
        self._panel_window = self._panel_canvas.create_window(
            (0, 0), window=self.panel, anchor=tk.NW
        )

        # Ajustar el scrollregion cuando cambia el tamaño del frame
        self.panel.bind("<Configure>", self._on_panel_configure)
        self._panel_canvas.bind("<Configure>", self._on_panel_canvas_configure)

        # Scroll con rueda del ratón
        self._panel_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._construir_panel()

    # ──────────────────────────────────────────────
    # Helpers para el scroll del panel lateral
    # ──────────────────────────────────────────────

    def _on_panel_configure(self, event):
        """Actualiza la scrollregion cuando el contenido del panel cambia de tamaño."""
        self._panel_canvas.configure(
            scrollregion=self._panel_canvas.bbox("all")
        )

    def _on_panel_canvas_configure(self, event):
        """Hace que el frame interno tenga siempre el ancho del canvas."""
        self._panel_canvas.itemconfig(self._panel_window, width=event.width)

    def _on_mousewheel(self, event):
        """Desplaza el panel con la rueda del ratón (solo si el cursor está sobre él)."""
        self._panel_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _construir_panel(self):
        """Construye el panel lateral con controles."""
        p = self.panel

        # ── Sección: Configuración ──
        self._seccion(p, "CONFIGURACIÓN")

        f_tam = tk.Frame(p, bg=COLOR_PANEL)
        f_tam.pack(fill=tk.X, pady=4)
        tk.Label(f_tam, text="Tamaño:", bg=COLOR_PANEL, fg=COLOR_TEXTO,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        for tam in (4, 6, 8):
            tk.Radiobutton(
                f_tam, text=f"{tam}×{tam}", variable=self.n, value=tam,
                command=self._cambiar_tamano,
                bg=COLOR_PANEL, fg=COLOR_TEXTO,
                selectcolor=COLOR_ACENTO,
                activebackground=COLOR_PANEL,
                font=("Segoe UI", 10)
            ).pack(side=tk.LEFT, padx=4)

        self._boton(p, "🎲 Generar rejilla de ejemplo", self._generar_ejemplo)
        self._boton(p, "🗑️ Limpiar huecos", self._limpiar_huecos)

        # Validación
        self.lbl_validacion = tk.Label(
            p, text="", bg=COLOR_PANEL, fg="#fbbf24",
            font=("Segoe UI", 9), wraplength=240, justify=tk.LEFT
        )
        self.lbl_validacion.pack(fill=tk.X, pady=4)

        # ── Sección: Guardar / Cargar ──
        self._seccion(p, "REJILLA")
        f_gc = tk.Frame(p, bg=COLOR_PANEL)
        f_gc.pack(fill=tk.X, pady=2)
        self._boton_frame(f_gc, "💾 Guardar", self._guardar_rejilla, side=tk.LEFT)
        self._boton_frame(f_gc, "📂 Cargar", self._cargar_rejilla, side=tk.LEFT)

        # ── Sección: Cifrado ──
        self._seccion(p, "CIFRADO")
        tk.Label(p, text="Mensaje:", bg=COLOR_PANEL, fg=COLOR_TEXTO,
                 font=("Segoe UI", 10)).pack(anchor=tk.W)
        self.entry_mensaje = tk.Text(
            p, height=3, width=28,
            bg=COLOR_CELDA, fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            font=("Segoe UI", 10),
            relief=tk.FLAT, padx=6, pady=4
        )
        self.entry_mensaje.pack(fill=tk.X, pady=4)

        self._boton(p, "🔒 Cifrar", self._iniciar_cifrado)

        # ── Sección: Descifrado ──
        self._seccion(p, "DESCIFRADO")
        tk.Label(p, text="Pega la matriz cifrada (letras separadas por espacios, una fila por línea):",
                 bg=COLOR_PANEL, fg=COLOR_TEXTO,
                 font=("Segoe UI", 9), wraplength=240, justify=tk.LEFT).pack(anchor=tk.W)
        self.entry_matriz = tk.Text(
            p, height=5, width=28,
            bg=COLOR_CELDA, fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            font=("Courier New", 10),
            relief=tk.FLAT, padx=6, pady=4
        )
        self.entry_matriz.pack(fill=tk.X, pady=4)
        self._boton(p, "🔓 Descifrar", self._iniciar_descifrado)

        # ── Sección: Animación ──
        self._seccion(p, "ANIMACIÓN")
        f_vel = tk.Frame(p, bg=COLOR_PANEL)
        f_vel.pack(fill=tk.X, pady=2)
        tk.Label(f_vel, text="Velocidad:", bg=COLOR_PANEL, fg=COLOR_TEXTO,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        tk.Scale(
            f_vel, from_=200, to=2000, orient=tk.HORIZONTAL,
            variable=self.velocidad, bg=COLOR_PANEL, fg=COLOR_TEXTO,
            highlightthickness=0, troughcolor=COLOR_CELDA,
            length=140
        ).pack(side=tk.LEFT)

        f_anim = tk.Frame(p, bg=COLOR_PANEL)
        f_anim.pack(fill=tk.X, pady=2)
        self._boton_frame(f_anim, "⏮ Inicio", self._reset_animacion, side=tk.LEFT)
        self._boton_frame(f_anim, "▶ Paso", self._paso_siguiente, side=tk.LEFT)

        self._boton(p, "▶▶ Reproducir todo", self._reproducir_todo)

        # ── Resultado ──
        self._seccion(p, "RESULTADO")
        self.lbl_resultado = tk.Label(
            p, text="", bg=COLOR_PANEL, fg=COLOR_ACENTO2,
            font=("Courier New", 11, "bold"), wraplength=240, justify=tk.LEFT
        )
        self.lbl_resultado.pack(fill=tk.X, pady=4)

        self.lbl_paso_info = tk.Label(
            p, text="", bg=COLOR_PANEL, fg=COLOR_TEXTO,
            font=("Segoe UI", 9), wraplength=240, justify=tk.LEFT
        )
        self.lbl_paso_info.pack(fill=tk.X)

    # ──────────────────────────────────────────────
    # Helpers de UI
    # ──────────────────────────────────────────────

    def _seccion(self, parent, texto):
        tk.Label(
            parent, text=texto,
            bg=COLOR_PANEL, fg=COLOR_ACENTO,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor=tk.W, pady=(10, 2))
        tk.Frame(parent, bg=COLOR_ACENTO, height=1).pack(fill=tk.X)

    def _boton(self, parent, texto, comando):
        b = tk.Button(
            parent, text=texto, command=comando,
            bg=COLOR_BOTON, fg=COLOR_TEXTO,
            activebackground=COLOR_BOTON_HOVER,
            activeforeground=COLOR_TEXTO,
            font=("Segoe UI", 10),
            relief=tk.FLAT, padx=8, pady=5,
            cursor="hand2"
        )
        b.pack(fill=tk.X, pady=2)
        return b

    def _boton_frame(self, parent, texto, comando, side=tk.LEFT):
        b = tk.Button(
            parent, text=texto, command=comando,
            bg=COLOR_BOTON, fg=COLOR_TEXTO,
            activebackground=COLOR_BOTON_HOVER,
            activeforeground=COLOR_TEXTO,
            font=("Segoe UI", 9),
            relief=tk.FLAT, padx=6, pady=4,
            cursor="hand2"
        )
        b.pack(side=side, padx=2, pady=2)
        return b

    # ──────────────────────────────────────────────
    # Dibujo del canvas
    # ──────────────────────────────────────────────

    def _dibujar_rejilla(self, huecos_resaltados=None, letras_extra=None, angulo_rotacion=0):
        """
        Dibuja la rejilla en el canvas.
        huecos_resaltados: conjunto de celdas a resaltar con color activo.
        letras_extra: dict {(fila, col): letra} para mostrar sobre las celdas.
        angulo_rotacion: ángulo actual de rotación para el indicador visual.
        """
        self.canvas.delete("all")
        n = self.n.get()
        tam = TAMANIO_CELDA
        offset_x = PADDING_CANVAS
        offset_y = PADDING_CANVAS + 50  # espacio para el indicador de rotación

        # Indicador de rotación
        self.canvas.create_text(
            offset_x, PADDING_CANVAS,
            text=f"Rotación: {angulo_rotacion}°",
            fill=COLOR_ACENTO2,
            font=("Segoe UI", 12, "bold"),
            anchor=tk.NW
        )

        if huecos_resaltados is None:
            huecos_resaltados = set()
        if letras_extra is None:
            letras_extra = {}

        for fila in range(n):
            for col in range(n):
                x1 = offset_x + col * tam
                y1 = offset_y + fila * tam
                x2 = x1 + tam
                y2 = y1 + tam
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                celda = (fila, col)

                if celda in huecos_resaltados:
                    # Hueco activo (resaltado durante animación)
                    color_fondo = COLOR_ACTIVO
                    color_borde = COLOR_ACTIVO_BORDE
                elif celda in self.huecos:
                    # Hueco marcado por el usuario (posición 0°)
                    color_fondo = COLOR_HUECO
                    color_borde = COLOR_HUECO_BORDE
                elif celda in self.huecos_rotados and not self.pasos_animacion:
                    # Posición que ocupa este hueco en alguna rotación (90°/180°/270°)
                    color_fondo = COLOR_ROTACION
                    color_borde = COLOR_ROTACION_BORDE
                else:
                    color_fondo = COLOR_CELDA
                    color_borde = COLOR_CELDA_BORDE

                self.canvas.create_rectangle(
                    x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                    fill=color_fondo, outline=color_borde, width=2,
                    tags=f"celda_{fila}_{col}"
                )

                # Etiqueta de rotación en celdas fantasma (90°/180°/270°)
                if celda in self.huecos_rotados and not self.pasos_animacion:
                    # Calcular qué ángulo de rotación corresponde a esta celda
                    angulo_label = self._angulo_de_celda_rotada(celda)
                    if angulo_label:
                        self.canvas.create_text(
                            cx, cy,
                            text=angulo_label,
                            fill=COLOR_ROTACION_BORDE,
                            font=("Segoe UI", 9, "bold")
                        )

                # Letra en la celda (de la matriz cifrada o del paso de animación)
                if celda in letras_extra and letras_extra[celda]:
                    self.canvas.create_text(
                        cx, cy,
                        text=letras_extra[celda],
                        fill=COLOR_LETRA,
                        font=("Segoe UI", 18, "bold")
                    )
                elif self.matriz_cifrada and self.matriz_cifrada[fila][col]:
                    self.canvas.create_text(
                        cx, cy,
                        text=self.matriz_cifrada[fila][col],
                        fill="#94a3b8",
                        font=("Segoe UI", 14)
                    )

        # Coordenadas (números de fila y columna)
        for i in range(n):
            self.canvas.create_text(
                offset_x + i * tam + tam // 2, offset_y - 12,
                text=str(i + 1),
                fill="#64748b",
                font=("Segoe UI", 9)
            )
            self.canvas.create_text(
                offset_x - 12, offset_y + i * tam + tam // 2,
                text=str(i + 1),
                fill="#64748b",
                font=("Segoe UI", 9)
            )

        # Dibujar ícono de rotación (flecha circular) si hay rotación activa
        if angulo_rotacion > 0:
            self._dibujar_flecha_rotacion(offset_x, offset_y, n, tam, angulo_rotacion)

    def _dibujar_flecha_rotacion(self, ox, oy, n, tam, angulo):
        """Dibuja una flecha indicando la rotación actual."""
        total_w = n * tam
        total_h = n * tam
        cx = ox + total_w + 40
        cy = oy + total_h // 2
        r = 25

        # Arco
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90, extent=-angulo,
            outline=COLOR_ACENTO2, width=3, style=tk.ARC
        )
        self.canvas.create_text(
            cx, cy + r + 14,
            text=f"{angulo}°",
            fill=COLOR_ACENTO2,
            font=("Segoe UI", 10, "bold")
        )

    # ──────────────────────────────────────────────
    # Eventos del canvas
    # ──────────────────────────────────────────────

    def _clic_canvas(self, event):
        """Maneja el clic en el canvas para marcar/desmarcar huecos."""
        n = self.n.get()
        tam = TAMANIO_CELDA
        offset_x = PADDING_CANVAS
        offset_y = PADDING_CANVAS + 50

        col = (event.x - offset_x) // tam
        fila = (event.y - offset_y) // tam

        if 0 <= fila < n and 0 <= col < n:
            celda = (fila, col)
            if celda in self.huecos:
                self.huecos.discard(celda)
            else:
                self.huecos.add(celda)
            self._actualizar_rotaciones_preview()
            self._dibujar_rejilla()
            self._actualizar_validacion()

    # ──────────────────────────────────────────────
    # Acciones de configuración
    # ──────────────────────────────────────────────

    def _cambiar_tamano(self):
        self.huecos.clear()
        self.matriz_cifrada = None
        self.pasos_animacion = []
        self.paso_actual = 0
        self.lbl_resultado.config(text="")
        self.lbl_validacion.config(text="")
        self._dibujar_rejilla()

    def _generar_ejemplo(self):
        n = self.n.get()
        from logica.rejilla import generar_rejilla_ejemplo
        self.huecos = generar_rejilla_ejemplo(n)
        self.matriz_cifrada = None
        self.pasos_animacion = []
        self.paso_actual = 0
        self._actualizar_rotaciones_preview()
        self._dibujar_rejilla()
        self._actualizar_validacion()

    def _limpiar_huecos(self):
        self.huecos.clear()
        self.huecos_rotados.clear()
        self._rotaciones_por_angulo = {}
        self.matriz_cifrada = None
        self.pasos_animacion = []
        self.paso_actual = 0
        self.lbl_resultado.config(text="")
        self.lbl_validacion.config(text="")
        self._dibujar_rejilla()

    def _actualizar_rotaciones_preview(self):
        """
        Calcula qué celdas quedan ocupadas al rotar los huecos actuales
        90°, 180° y 270°. Se muestran en verde para que el usuario vea
        el efecto de sus huecos en todas las rotaciones.
        """
        from logica.rejilla import obtener_todas_rotaciones
        n = self.n.get()
        self.huecos_rotados = set()
        self._rotaciones_por_angulo = {}   # {celda: "90°" / "180°" / "270°"}

        if not self.huecos:
            return

        rotaciones = obtener_todas_rotaciones(self.huecos, n)
        angulos = [90, 180, 270]

        for idx, rot in enumerate(rotaciones[1:]):   # omitir la rotación 0° (son los huecos mismos)
            angulo_str = f"{angulos[idx]}°"
            for celda in rot:
                if celda not in self.huecos:         # no pintar encima del hueco original
                    self.huecos_rotados.add(celda)
                    # Guardar solo el primer ángulo que ocupa esa celda
                    if celda not in self._rotaciones_por_angulo:
                        self._rotaciones_por_angulo[celda] = angulo_str

    def _angulo_de_celda_rotada(self, celda):
        """Devuelve el ángulo de rotación que produce esta celda, o None."""
        return getattr(self, '_rotaciones_por_angulo', {}).get(celda, None)

    def _actualizar_validacion(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if valida:
            self.lbl_validacion.config(
                text="✓ Rejilla válida",
                fg="#4ade80"
            )
        else:
            self.lbl_validacion.config(text=f"✗ {msg}", fg="#f87171")

    # ──────────────────────────────────────────────
    # Guardar / Cargar
    # ──────────────────────────────────────────────

    def _guardar_rejilla(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if not valida:
            messagebox.showerror("Rejilla inválida", msg)
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            title="Guardar rejilla"
        )
        if ruta:
            guardar_rejilla(self.huecos, n, ruta)
            messagebox.showinfo("Guardado", f"Rejilla guardada en:\n{ruta}")

    def _cargar_rejilla(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            title="Cargar rejilla"
        )
        if ruta:
            try:
                huecos, n = cargar_rejilla(ruta)
                self.n.set(n)
                self.huecos = huecos
                self.matriz_cifrada = None
                self.pasos_animacion = []
                self._dibujar_rejilla()
                self._actualizar_validacion()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la rejilla:\n{e}")

    # ──────────────────────────────────────────────
    # Cifrado
    # ──────────────────────────────────────────────

    def _iniciar_cifrado(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if not valida:
            messagebox.showerror("Rejilla inválida", msg)
            return

        mensaje = self.entry_mensaje.get("1.0", tk.END).strip()
        if not mensaje:
            messagebox.showwarning("Sin mensaje", "Escribe un mensaje para cifrar.")
            return

        matriz, pasos, texto_usado = cifrar(mensaje, self.huecos, n)
        self.matriz_cifrada = matriz
        self.pasos_animacion = pasos
        self.paso_actual = -1  # empezamos antes del paso 0

        # Mostrar resultado en el entry de matriz
        self.entry_matriz.delete("1.0", tk.END)
        for fila in matriz:
            self.entry_matriz.insert(tk.END, ' '.join(fila) + '\n')

        # Resultado final
        texto_cifrado = ''.join(''.join(f) for f in matriz)
        self.lbl_resultado.config(
            text=f"Cifrado:\n{texto_cifrado}"
        )
        self.lbl_paso_info.config(
            text=f"Mensaje usado: {texto_usado}\nPresiona ▶ Paso para animar."
        )
        self._dibujar_rejilla()

    # ──────────────────────────────────────────────
    # Descifrado
    # ──────────────────────────────────────────────

    def _iniciar_descifrado(self):
        n = self.n.get()
        valida, msg = validar_rejilla(self.huecos, n)
        if not valida:
            messagebox.showerror("Rejilla inválida", msg)
            return

        texto_matriz = self.entry_matriz.get("1.0", tk.END).strip()
        if not texto_matriz:
            messagebox.showwarning("Sin matriz", "Pega la matriz cifrada en el campo.")
            return

        # Parsear la matriz
        try:
            filas = texto_matriz.strip().split('\n')
            matriz = []
            for fila_str in filas:
                fila = fila_str.strip().upper().split()
                matriz.append(fila)
            if len(matriz) != n:
                raise ValueError(f"Se esperan {n} filas, se encontraron {len(matriz)}.")
            for i, fila in enumerate(matriz):
                if len(fila) != n:
                    raise ValueError(f"Fila {i+1} tiene {len(fila)} columnas, se esperan {n}.")
        except Exception as e:
            messagebox.showerror("Formato inválido", str(e))
            return

        self.matriz_cifrada = matriz
        mensaje, pasos = descifrar(matriz, self.huecos, n)
        self.pasos_animacion = pasos
        self.paso_actual = -1

        self.lbl_resultado.config(text=f"Descifrado:\n{mensaje}")
        self.lbl_paso_info.config(text="Presiona ▶ Paso para animar.")
        self._dibujar_rejilla()

    # ──────────────────────────────────────────────
    # Animación
    # ──────────────────────────────────────────────

    def _reset_animacion(self):
        self.animando = False
        self.paso_actual = -1
        self._dibujar_rejilla()
        self.lbl_paso_info.config(text="Animación reiniciada.")

    def _paso_siguiente(self):
        if not self.pasos_animacion:
            messagebox.showinfo("Sin pasos", "Cifra o descifra un mensaje primero.")
            return

        self.paso_actual += 1
        if self.paso_actual >= len(self.pasos_animacion):
            self.paso_actual = len(self.pasos_animacion) - 1
            self.lbl_paso_info.config(text="Animación completada.")
            return

        self._mostrar_paso(self.paso_actual)

    def _mostrar_paso(self, idx):
        paso = self.pasos_animacion[idx]
        angulo = paso['rotacion']
        huecos_activos = set(tuple(h) for h in paso['huecos'])
        letras = {tuple(k): v for k, v in paso['letras'].items()}

        self._dibujar_rejilla(
            huecos_resaltados=huecos_activos,
            letras_extra=letras,
            angulo_rotacion=angulo
        )

        letras_str = ' '.join(letras.values())
        self.lbl_paso_info.config(
            text=f"Paso {idx + 1}/4 — Rotación {angulo}°\n"
                 f"Letras visibles: {letras_str}\n"
                 f"Paso {idx + 1} de {len(self.pasos_animacion)}"
        )

    def _reproducir_todo(self):
        if not self.pasos_animacion:
            messagebox.showinfo("Sin pasos", "Cifra o descifra un mensaje primero.")
            return
        if self.animando:
            return

        self.animando = True
        self.paso_actual = -1
        self._animar_siguiente()

    def _animar_siguiente(self):
        if not self.animando:
            return

        self.paso_actual += 1
        if self.paso_actual >= len(self.pasos_animacion):
            self.animando = False
            self.lbl_paso_info.config(
                text=self.lbl_paso_info.cget("text") + "\n✓ Completado"
            )
            return

        self._mostrar_paso(self.paso_actual)
        self.after(self.velocidad.get(), self._animar_siguiente)

