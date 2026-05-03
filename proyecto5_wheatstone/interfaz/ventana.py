import tkinter as tk
from tkinter import ttk, messagebox
import math

from logica.engranajes import (
    cifrar_wheatstone, 
    descifrar_wheatstone, 
    normalizar_texto,
    DISCO_EXT, 
    DISCO_INT
)

# Paleta de colores (similar a proyectos anteriores)
C_FONDO     = "#0f172a"
C_PANEL     = "#1e293b"
C_PANEL2    = "#162032"
C_BORDE     = "#334155"
C_ACENTO    = "#8b5cf6"
C_ACENTO2   = "#22d3ee"
C_TEXTO     = "#e2e8f0"
C_SUB       = "#94a3b8"
C_BTN       = "#3730a3"
C_BTN2      = "#065f46"
C_BTN_HOV   = "#4338ca"
C_AGUJA_EXT = "#22d3ee"
C_AGUJA_INT = "#f59e0b"

class AplicacionWheatstone(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Criptógrafo de Wheatstone - Proyecto 5")
        self.configure(bg=C_FONDO)
        self.minsize(1050, 650)
        
        # Variables de estado y animación
        self.texto_entrada = tk.StringVar()
        self.modo = tk.StringVar(value="Cifrar")  # "Cifrar" o "Descifrar"
        self.velocidad = tk.IntVar(value=50)      # ms por frame
        
        # Posiciones reales en los discos (índices enteros)
        self.pos_ext = 0
        self.pos_int = 0
        
        # Posiciones de animación (flotantes, pueden crecer indefinidamente durante un avance para simular rotación continua)
        self.anim_ext = 0.0
        self.anim_int = 0.0
        self.destino_ext = 0.0
        self.destino_int = 0.0
        
        # Estado de ejecución
        self.pasos = []
        self.paso_actual = 0
        self.is_animating = False
        self.auto_play = False
        
        self._construir_ui()
        self._dibujar_ruedas()

    def _construir_ui(self):
        # Cabecera
        cab = tk.Frame(self, bg=C_FONDO, pady=10)
        cab.pack(fill=tk.X, padx=15)
        tk.Label(cab, text="⚙️ Criptógrafo de Wheatstone",
                 font=("Segoe UI", 16, "bold"), bg=C_FONDO, fg=C_ACENTO
                 ).pack(side=tk.LEFT)
        tk.Label(cab,
                 text="El desfase mecánico (27 vs 26 posiciones) asegura un cifrado poligráfico.",
                 font=("Segoe UI", 10), bg=C_FONDO, fg=C_SUB
                 ).pack(side=tk.LEFT, padx=15)

        main = tk.Frame(self, bg=C_FONDO)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Izquierda: Canvas (Ruedas)
        izq = tk.Frame(main, bg=C_PANEL, padx=10, pady=10)
        izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(izq, bg=C_FONDO, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._dibujar_ruedas())

        # Derecha: Panel de Control y Resultados
        der = tk.Frame(main, bg=C_PANEL, padx=15, pady=15, width=420)
        der.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        der.pack_propagate(False)
        
        self._construir_controles(der)

    def _construir_controles(self, parent):
        # -- Entrada --
        tk.Label(parent, text="TEXTO PLANO / CIFRADO", bg=C_PANEL, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 5))
        
        self.entry_texto = tk.Entry(parent, textvariable=self.texto_entrada, 
                                   bg=C_PANEL2, fg=C_TEXTO, insertbackground=C_TEXTO,
                                   font=("Segoe UI", 12), relief=tk.FLAT)
        self.entry_texto.pack(fill=tk.X, ipady=4, pady=5)
        
        # -- Botones de Acción --
        f_btns = tk.Frame(parent, bg=C_PANEL)
        f_btns.pack(fill=tk.X, pady=5)
        
        self._btn(f_btns, "🔒 Iniciar Cifrado", self._iniciar_cifrado, C_BTN2, tk.LEFT)
        self._btn(f_btns, "🔓 Iniciar Descifrado", self._iniciar_descifrado, C_BTN, tk.LEFT)
        
        # -- Controles de Animación --
        tk.Label(parent, text="CONTROLES DE ANIMACIÓN", bg=C_PANEL, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(15, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 5))
        
        f_anim = tk.Frame(parent, bg=C_PANEL)
        f_anim.pack(fill=tk.X, pady=5)
        self._btn(f_anim, "▶ Paso a Paso", self._siguiente_paso, C_BTN, tk.LEFT)
        self._btn(f_anim, "▶▶ Auto", self._play_auto, C_BTN, tk.LEFT)
        self._btn(f_anim, "⏮ Reset", self._reset, C_BORDE, tk.LEFT)
        
        # Velocidad
        f_vel = tk.Frame(parent, bg=C_PANEL)
        f_vel.pack(fill=tk.X, pady=5)
        tk.Label(f_vel, text="Lento", bg=C_PANEL, fg=C_SUB, font=("Segoe UI", 8)).pack(side=tk.LEFT)
        tk.Scale(f_vel, from_=100, to=10, variable=self.velocidad, orient=tk.HORIZONTAL,
                 bg=C_PANEL, fg=C_TEXTO, highlightthickness=0, showvalue=0).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Label(f_vel, text="Rápido", bg=C_PANEL, fg=C_SUB, font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # -- Casos Didácticos --
        tk.Label(parent, text="DEMOSTRACIÓN DIDÁCTICA", bg=C_PANEL, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(15, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 5))
        
        f_demo = tk.Frame(parent, bg=C_PANEL)
        f_demo.pack(fill=tk.X)
        self._btn(f_demo, "Test 'AAAA'", lambda: self._cargar_demo("AAAA"), C_PANEL2, tk.LEFT)
        self._btn(f_demo, "Test 'HOLA MUNDO'", lambda: self._cargar_demo("HOLA MUNDO"), C_PANEL2, tk.LEFT)

        # -- Resultados (Tabla) --
        tk.Label(parent, text="TRAZA DE EJECUCIÓN", bg=C_PANEL, fg=C_ACENTO,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(15, 2))
        tk.Frame(parent, bg=C_BORDE, height=1).pack(fill=tk.X, pady=(0, 5))
        
        self.lbl_resultado_final = tk.Label(parent, text="", bg=C_PANEL, fg=C_ACENTO2,
                                            font=("Courier New", 12, "bold"), wraplength=380, justify=tk.LEFT)
        self.lbl_resultado_final.pack(anchor=tk.W, pady=(0, 5))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("W.Treeview", background=C_PANEL2, foreground=C_TEXTO, 
                        fieldbackground=C_PANEL2, rowheight=24, font=("Segoe UI", 9))
        style.configure("W.Treeview.Heading", background=C_BORDE, foreground=C_TEXTO, font=("Segoe UI", 9, "bold"))
        style.map("W.Treeview", background=[("selected", C_ACENTO)])

        cols = ("Letra Org.", "Pos Ext", "Pos Int", "Desfase", "Letra Cif.")
        self.tabla = ttk.Treeview(parent, columns=cols, show="headings", style="W.Treeview", height=8)
        for c in cols:
            self.tabla.heading(c, text=c)
            self.tabla.column(c, anchor=tk.CENTER, width=70)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        # Desfase Label
        self.lbl_desfase = tk.Label(parent, text="Desfase actual: 0 posiciones", 
                                    bg=C_PANEL, fg=C_ACENTO2, font=("Segoe UI", 10, "bold"))
        self.lbl_desfase.pack(anchor=tk.W, pady=(10, 0))

    def _btn(self, parent, text, cmd, bg, side):
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=C_TEXTO,
                      activebackground=C_BTN_HOV, activeforeground=C_TEXTO,
                      font=("Segoe UI", 9), relief=tk.FLAT, padx=8, pady=4, cursor="hand2")
        b.pack(side=side, padx=2)

    # ──────────────────────────────────────────────
    # Dibujo de Ruedas y Agujas
    # ──────────────────────────────────────────────
    def _dibujar_ruedas(self):
        self.canvas.delete("all")
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return
            
        cx, cy = w / 2, h / 2
        r_ext = min(cx, cy) * 0.85
        r_int = r_ext * 0.70
        
        self.cx = cx
        self.cy = cy
        self.r_ext = r_ext
        self.r_int = r_int
        
        # Dibujar Círculos
        self.canvas.create_oval(cx - r_ext, cy - r_ext, cx + r_ext, cy + r_ext, 
                                outline=C_BORDE, width=2, fill=C_PANEL2)
        self.canvas.create_oval(cx - r_int, cy - r_int, cx + r_int, cy + r_int, 
                                outline=C_BORDE, width=2, fill=C_FONDO)
        
        # Dibujar Letras Exterior (27 pos)
        for i, char in enumerate(DISCO_EXT):
            angulo = -math.pi/2 + (i * 2 * math.pi / 27)
            x = cx + r_ext * 0.88 * math.cos(angulo)
            y = cy + r_ext * 0.88 * math.sin(angulo)
            # Marcas divisorias
            x_mark_in = cx + r_ext * 0.95 * math.cos(angulo + math.pi/27)
            y_mark_in = cy + r_ext * 0.95 * math.sin(angulo + math.pi/27)
            x_mark_out = cx + r_ext * math.cos(angulo + math.pi/27)
            y_mark_out = cy + r_ext * math.sin(angulo + math.pi/27)
            self.canvas.create_line(x_mark_in, y_mark_in, x_mark_out, y_mark_out, fill=C_BORDE)
            
            self.canvas.create_text(x, y, text=char, fill=C_TEXTO, font=("Segoe UI", 11, "bold"))
            
        # Dibujar Letras Interior (26 pos)
        for i, char in enumerate(DISCO_INT):
            angulo = -math.pi/2 + (i * 2 * math.pi / 26)
            x = cx + r_int * 0.82 * math.cos(angulo)
            y = cy + r_int * 0.82 * math.sin(angulo)
            # Marcas divisorias
            x_mark_in = cx + r_int * 0.90 * math.cos(angulo + math.pi/26)
            y_mark_in = cy + r_int * 0.90 * math.sin(angulo + math.pi/26)
            x_mark_out = cx + r_int * math.cos(angulo + math.pi/26)
            y_mark_out = cy + r_int * math.sin(angulo + math.pi/26)
            self.canvas.create_line(x_mark_in, y_mark_in, x_mark_out, y_mark_out, fill=C_BORDE)
            
            self.canvas.create_text(x, y, text=char, fill=C_SUB, font=("Segoe UI", 10))
            
        # Centro
        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=C_BORDE, outline="")
        
        # Dibujar Agujas basadas en anim_ext y anim_int
        self._dibujar_agujas()

    def _dibujar_agujas(self):
        self.canvas.delete("agujas")
        if not hasattr(self, 'cx'):
            return
            
        ang_ext = -math.pi/2 + (self.anim_ext * 2 * math.pi / 27)
        ang_int = -math.pi/2 + (self.anim_int * 2 * math.pi / 26)
        
        # Aguja Interior
        x_int = self.cx + self.r_int * 0.95 * math.cos(ang_int)
        y_int = self.cy + self.r_int * 0.95 * math.sin(ang_int)
        self.canvas.create_line(self.cx, self.cy, x_int, y_int, 
                                fill=C_AGUJA_INT, width=3, arrow=tk.LAST, tags="agujas")
                                
        # Aguja Exterior
        x_ext = self.cx + self.r_ext * 0.98 * math.cos(ang_ext)
        y_ext = self.cy + self.r_ext * 0.98 * math.sin(ang_ext)
        self.canvas.create_line(self.cx, self.cy, x_ext, y_ext, 
                                fill=C_AGUJA_EXT, width=3, arrow=tk.LAST, tags="agujas")

    # ──────────────────────────────────────────────
    # Lógica de Ejecución y Animación
    # ──────────────────────────────────────────────
    def _cargar_demo(self, texto):
        self.texto_entrada.set(texto)
        self._iniciar_cifrado()

    def _iniciar_cifrado(self):
        texto = self.entry_texto.get()
        if not texto: return
        self.modo.set("Cifrar")
        self._reset_estado()
        
        self.resultado_final, self.pasos = cifrar_wheatstone(texto, self.pos_ext, self.pos_int)
        self._limpiar_tabla()
        self._play_auto()

    def _iniciar_descifrado(self):
        texto = self.entry_texto.get()
        if not texto: return
        self.modo.set("Descifrar")
        self._reset_estado()
        
        self.resultado_final, self.pasos = descifrar_wheatstone(texto, self.pos_ext, self.pos_int)
        self._limpiar_tabla()
        self._play_auto()

    def _reset_estado(self):
        self.pos_ext = 0
        self.pos_int = 0
        self.anim_ext = 0.0
        self.anim_int = 0.0
        self.destino_ext = 0.0
        self.destino_int = 0.0
        self.paso_actual = 0
        self.is_animating = False
        self.auto_play = False
        self.resultado_final = ""
        self.lbl_resultado_final.config(text="")
        self._dibujar_agujas()
        self._limpiar_tabla()
        self.lbl_desfase.config(text="Desfase actual: 0 posiciones")

    def _reset(self):
        self.entry_texto.delete(0, tk.END)
        self._reset_estado()

    def _limpiar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def _siguiente_paso(self):
        if self.is_animating or not self.pasos:
            return
            
        if self.paso_actual >= len(self.pasos):
            self.lbl_resultado_final.config(text=f"Resultado: {self.resultado_final}")
            messagebox.showinfo("Fin", "Se ha completado el procesamiento del texto.")
            self.auto_play = False
            return
            
        self.is_animating = True
        paso = self.pasos[self.paso_actual]
        
        avance = paso['avance']
        self.destino_ext = self.anim_ext + avance
        self.destino_int = self.anim_int + avance
        
        self.paso_actual += 1
        self._tick_animacion(paso)

    def _play_auto(self):
        if not self.pasos: return
        if self.auto_play: return
        self.auto_play = True
        self._siguiente_paso()

    def _tick_animacion(self, paso_info):
        step_size = max(0.5, 30.0 / self.velocidad.get())  # Velocidad dinámica
        
        if self.anim_ext < self.destino_ext:
            self.anim_ext = min(self.anim_ext + step_size, self.destino_ext)
            self.anim_int = min(self.anim_int + step_size, self.destino_int)
            self._dibujar_agujas()
            self.after(20, lambda: self._tick_animacion(paso_info))
        else:
            # Animación de este paso completada
            self.anim_ext = self.destino_ext
            self.anim_int = self.destino_int
            
            # Normalizar para evitar números gigantescos si hay muchos pasos
            # Pero solo a nivel lógico, para que el giro se vea coherente.
            # En realidad, si dejamos que crezca, math.sin/cos manejan bien ángulos grandes.
            
            self._dibujar_agujas()
            self._agregar_resultado_tabla(paso_info)
            self.is_animating = False
            
            if self.auto_play:
                # Pausa breve antes del siguiente paso
                self.after(300, self._siguiente_paso)

    def _agregar_resultado_tabla(self, p):
        if self.modo.get() == "Cifrar":
            l_orig = p['letra_clara']
            l_cif = p['letra_cifrada']
        else:
            l_orig = p['letra_cifrada']   # entrada: la letra cifrada
            l_cif = p['letra_clara']      # salida:  la letra descifrada
            
        desfase = (p['pos_ext_post'] - p['pos_int_post']) % 26
            
        item_id = self.tabla.insert("", tk.END, values=(
            l_orig,
            f"{p['pos_ext_post']:02d} ({DISCO_EXT[p['pos_ext_post']]})",
            f"{p['pos_int_post']:02d} ({DISCO_INT[p['pos_int_post']]})",
            f"Δ {desfase}",
            l_cif
        ))
        self.tabla.see(item_id)
        self.lbl_desfase.config(text=f"Desfase actual: {desfase} posiciones")

if __name__ == "__main__":
    app = AplicacionWheatstone()
    app.mainloop()

