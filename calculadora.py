import tkinter as tk
import math
import sys
import os
import ctypes
from PIL import Image, ImageTk
from blackjack import VentanaBlackjack, obtener_ruta_asset

# Paleta de colores oficial estilo Windows 11 Dark
COLOR_FONDO = "#202020"
COLOR_BOTON_NUM = "#3b3b3b"
COLOR_BOTON_NUM_HOVER = "#454545"
COLOR_BOTON_FUNC = "#2d2d2d"
COLOR_BOTON_FUNC_HOVER = "#383838"
COLOR_IGUAL = "#2cd246"  # Verde neón estilo Windows
COLOR_IGUAL_HOVER = "#26b83d"
COLOR_TEXTO = "#ffffff"
COLOR_TEXTO_DESACTIVADO = "#7a7a7a"

class CalculadoraWindows:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora")
        self.root.geometry("340x510")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_FONDO)

        # Cargar icono personalizado para la ventana y la barra de tareas mediante Pillow
        ruta_icono = obtener_ruta_asset("assets/icono.ico")
        if os.path.exists(ruta_icono):
            try:
                img_pil = Image.open(ruta_icono)
                self.icono_app = ImageTk.PhotoImage(img_pil)
                self.root.iconphoto(True, self.icono_app)
            except Exception:
                try:
                    self.root.iconbitmap(ruta_icono)
                except Exception:
                    pass

        self.expresion = ""

        # Configurar filas y columnas del Grid principal
        self.root.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Fila 0: Cabecera | Fila 1: Historial | Fila 2: Pantalla principal
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)

        # Filas 3 a 8 para los botones
        for r in range(3, 9):
            self.root.rowconfigure(r, weight=1)

        self.crear_interfaz()

    def crear_interfaz(self):
        # 1. Cabecera superior "Estándar"
        frame_cabecera = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_cabecera.grid(row=0, column=0, columnspan=4, sticky="nw", padx=15, pady=(12, 0))

        lbl_titulo = tk.Label(frame_cabecera, text="Estándar", font=("Segoe UI", 16, "bold"), fg=COLOR_TEXTO, bg=COLOR_FONDO)
        lbl_titulo.pack(side="left")

        # 2. Historial secundario (operación previa)
        self.lbl_historial = tk.Label(
            self.root, text="", font=("Segoe UI", 10), fg=COLOR_TEXTO_DESACTIVADO, bg=COLOR_FONDO, anchor="e"
        )
        self.lbl_historial.grid(row=1, column=0, columnspan=4, padx=15, sticky="se")

        # 3. Pantalla de entrada principal
        self.pantalla = tk.Entry(
            self.root, font=("Segoe UI", 32, "bold"), justify="right",
            bd=0, bg=COLOR_FONDO, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO
        )
        self.pantalla.grid(row=2, column=0, columnspan=4, padx=15, pady=(0, 10), sticky="nsew")
        self.pantalla.insert(0, "0")

        # 4. Rejilla de botones (6 filas x 4 columnas)
        botones = [
            # Fila 3
            ('%', 3, 0, COLOR_BOTON_FUNC), ('CE', 3, 1, COLOR_BOTON_FUNC),
            ('C', 3, 2, COLOR_BOTON_FUNC), ('⌫', 3, 3, COLOR_BOTON_FUNC),
            # Fila 4
            ('¹/x', 4, 0, COLOR_BOTON_FUNC), ('x²', 4, 1, COLOR_BOTON_FUNC),
            ('√x', 4, 2, COLOR_BOTON_FUNC), ('÷', 4, 3, COLOR_BOTON_FUNC),
            # Fila 5
            ('7', 5, 0, COLOR_BOTON_NUM), ('8', 5, 1, COLOR_BOTON_NUM),
            ('9', 5, 2, COLOR_BOTON_NUM), ('×', 5, 3, COLOR_BOTON_FUNC),
            # Fila 6
            ('4', 6, 0, COLOR_BOTON_NUM), ('5', 6, 1, COLOR_BOTON_NUM),
            ('6', 6, 2, COLOR_BOTON_NUM), ('-', 6, 3, COLOR_BOTON_FUNC),
            # Fila 7
            ('1', 7, 0, COLOR_BOTON_NUM), ('2', 7, 1, COLOR_BOTON_NUM),
            ('3', 7, 2, COLOR_BOTON_NUM), ('+', 7, 3, COLOR_BOTON_FUNC),
            # Fila 8
            ('+/-', 8, 0, COLOR_BOTON_NUM), ('0', 8, 1, COLOR_BOTON_NUM),
            ('.', 8, 2, COLOR_BOTON_NUM), ('=', 8, 3, COLOR_IGUAL)
        ]

        for (texto, fila, columna, color) in botones:
            fg_color = "#000000" if texto == '=' else COLOR_TEXTO
            
            btn = tk.Button(
                self.root, text=texto, font=("Segoe UI", 12 if len(texto) > 1 else 14),
                bg=color, fg=fg_color, bd=0, relief="flat", activebackground=color, activeforeground=fg_color,
                command=lambda t=texto: self.al_presionar_boton(t)
            )
            
            btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_hover(b, c, True))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_hover(b, c, False))
            
            btn.grid(row=fila, column=columna, padx=2, pady=2, sticky="nsew")

    def on_hover(self, boton, color_base, entra):
        if color_base == COLOR_BOTON_NUM:
            boton.config(bg=COLOR_BOTON_NUM_HOVER if entra else COLOR_BOTON_NUM)
        elif color_base == COLOR_BOTON_FUNC:
            boton.config(bg=COLOR_BOTON_FUNC_HOVER if entra else COLOR_BOTON_FUNC)
        elif color_base == COLOR_IGUAL:
            boton.config(bg=COLOR_IGUAL_HOVER if entra else COLOR_IGUAL)

    def actualizar_pantalla_texto(self, texto):
        self.pantalla.delete(0, tk.END)
        self.pantalla.insert(0, str(texto))

    def al_presionar_boton(self, texto):
        if texto in '0123456789':
            if self.expresion == "0" or self.pantalla.get() == "Error":
                self.expresion = ""
            self.expresion += texto
            self.actualizar_pantalla_texto(self.expresion)

        elif texto == '.':
            if not self.expresion or self.expresion[-1] in '+-*/':
                self.expresion += "0."
            elif '.' not in self.expresion.split('+')[-1].split('-')[-1].split('*')[-1].split('/')[-1]:
                self.expresion += "."
            self.actualizar_pantalla_texto(self.expresion)

        elif texto in ['+', '-', '×', '÷']:
            op_map = {'×': '*', '÷': '/'}
            op = op_map.get(texto, texto)
            if self.expresion and self.expresion[-1] in '+-*/':
                self.expresion = self.expresion[:-1] + op
            elif self.expresion:
                self.expresion += op
            self.actualizar_pantalla_texto(self.expresion if self.expresion else "0")

        elif texto == 'C':
            self.expresion = ""
            self.lbl_historial.config(text="")
            self.actualizar_pantalla_texto("0")

        elif texto == 'CE':
            if self.expresion:
                indices = [self.expresion.rfind(op) for op in '+-*/']
                ultimo_op = max(indices)
                if ultimo_op != -1:
                    self.expresion = self.expresion[:ultimo_op + 1]
                else:
                    self.expresion = ""
            self.actualizar_pantalla_texto(self.expresion if self.expresion else "0")

        elif texto == '⌫':
            if self.expresion:
                self.expresion = self.expresion[:-1]
            self.actualizar_pantalla_texto(self.expresion if self.expresion else "0")

        elif texto == '+/-':
            if self.expresion:
                try:
                    val = float(eval(self.expresion))
                    val = -val
                    self.expresion = str(int(val) if val.is_integer() else val)
                    self.actualizar_pantalla_texto(self.expresion)
                except Exception:
                    pass

        elif texto == '%':
            if self.expresion:
                try:
                    val = float(eval(self.expresion)) / 100
                    self.expresion = str(int(val) if val.is_integer() else val)
                    self.actualizar_pantalla_texto(self.expresion)
                except Exception:
                    pass

        elif texto == '¹/x':
            if self.expresion:
                try:
                    val = float(eval(self.expresion))
                    if val != 0:
                        res = 1 / val
                        self.expresion = str(int(res) if res.is_integer() else res)
                        self.actualizar_pantalla_texto(self.expresion)
                    else:
                        self.actualizar_pantalla_texto("Error")
                        self.expresion = ""
                except Exception:
                    self.actualizar_pantalla_texto("Error")
                    self.expresion = ""

        elif texto == 'x²':
            if self.expresion:
                try:
                    val = float(eval(self.expresion)) ** 2
                    self.expresion = str(int(val) if val.is_integer() else val)
                    self.actualizar_pantalla_texto(self.expresion)
                except Exception:
                    self.actualizar_pantalla_texto("Error")
                    self.expresion = ""

        elif texto == '√x':
            if self.expresion:
                try:
                    val = float(eval(self.expresion))
                    if val >= 0:
                        res = math.sqrt(val)
                        self.expresion = str(int(res) if res.is_integer() else res)
                        self.actualizar_pantalla_texto(self.expresion)
                    else:
                        self.actualizar_pantalla_texto("Error")
                        self.expresion = ""
                except Exception:
                    self.actualizar_pantalla_texto("Error")
                    self.expresion = ""

        elif texto == '=':
            self.al_presionar_igual()

    def al_presionar_igual(self):
        if not self.expresion:
            return
        # Lanzar la apuesta de Blackjack
        VentanaBlackjack(self.root, al_ganar_callback=self.mostrar_resultado)

    def mostrar_resultado(self):
        try:
            self.lbl_historial.config(text=f"{self.expresion} =")
            resultado = eval(self.expresion)
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
            self.actualizar_pantalla_texto(resultado)
            self.expresion = str(resultado)
        except Exception:
            self.actualizar_pantalla_texto("Error")
            self.expresion = ""


if __name__ == "__main__":
    # Registrar el AppUserModelID para Windows ANTES de instanciar tk.Tk()
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mi.calculadora.troll.v1")
    except Exception:
        pass

    root = tk.Tk()
    app = CalculadoraWindows(root)
    root.mainloop()