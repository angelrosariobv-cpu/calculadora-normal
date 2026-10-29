import tkinter as tk
from tkinter import messagebox
import random
import sys
import os
from PIL import Image, ImageTk
import pygame  # Manejo de audio

def obtener_ruta_asset(ruta_relativa):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)

MAPA_IMAGENES = {
    'A': '01_kerenel_Cards.png',
    '2': '02_kerenel_Cards.png',
    '3': '03_kerenel_Cards.png',
    '4': '04_kerenel_Cards.png',
    '5': '05_kerenel_Cards.png',
    '6': '06_kerenel_Cards.png',
    '7': '07_kerenel_Cards.png',
    '8': '08_kerenel_Cards.png',
    '9': '09_kerenel_Cards.png',
    '10': '10_kerenel_Cards.png',
    'J': '11_kerenel_Cards.png',
    'Q': '12_kerenel_Cards.png',
    'K': '13_kerenel_Cards.png',
    'reverso': '28_kerenel_Cards.png'
}

class VentanaBlackjack(tk.Toplevel):
    def __init__(self, parent, al_ganar_callback):
        super().__init__(parent)
        self.parent = parent
        self.al_ganar_callback = al_ganar_callback

        self.title("Apuesta tu resultado")
        self.geometry("440x380")
        self.resizable(False, False)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self.perder("Cerraste la ventana de juego."))

        # Inicializar mezclador de audio de Pygame
        try:
            pygame.mixer.init()
            self.iniciar_musica_fondo()
        except Exception as e:
            print(f"Error al inicializar el audio: {e}")

        self.imagenes_cargadas = []
        self.items_cartas_canvas = []

        self.mazo = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        random.shuffle(self.mazo)

        self.mano_jugador = []
        self.mano_cpu = []

        self.crear_interfaz()
        self.actualizar_pantalla(mostrar_cpu_completo=False)
        
        self.deshabilitar_botones()
        self.after(300, self.iniciar_reparto_inicial)

    def reproducir_sfx(self, archivo):
        """Reproduce un efecto de sonido corto sin detener la música de fondo"""
        ruta = obtener_ruta_asset(f"assets/{archivo}")
        if os.path.exists(ruta):
            try:
                sound = pygame.mixer.Sound(ruta)
                sound.play()
            except Exception as e:
                print(f"Error al reproducir {archivo}: {e}")

    def iniciar_musica_fondo(self):
        """Inicia la música de fondo en bucle infinito"""
        ruta = obtener_ruta_asset("assets/musica de fondo.mp3")
        if os.path.exists(ruta):
            try:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play(-1)  # -1 indica repetición infinita
                pygame.mixer.music.set_volume(0.4)  # Volumen equilibrado al 40%
            except Exception as e:
                print(f"Error al cargar música de fondo: {e}")

    def detener_musica(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def sacar_carta(self):
        return self.mazo.pop()

    def calcular_puntos(self, mano):
        puntos = 0
        ases = 0
        valores = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        for carta in mano:
            if carta == 'A':
                ases += 1
            puntos += valores[carta]

        while puntos > 21 and ases > 0:
            puntos -= 10
            ases -= 1
        return puntos

    def obtener_imagen_carta(self, cve):
        nombre_archivo = MAPA_IMAGENES.get(cve, f"{cve}.png")
        ruta_img = obtener_ruta_asset(f"assets/{nombre_archivo}")
        if os.path.exists(ruta_img):
            try:
                img = tk.PhotoImage(file=ruta_img)
                self.imagenes_cargadas.append(img)
                return img
            except Exception as e:
                print(f"Error cargando {ruta_img}: {e}")
        return None

    def crear_interfaz(self):
        self.canvas = tk.Canvas(self, width=440, height=380, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # Fondo
        ruta_fondo = obtener_ruta_asset("assets/fondo.png")
        if os.path.exists(ruta_fondo):
            try:
                img_or = Image.open(ruta_fondo)
                img_res = img_or.resize((440, 380), Image.Resampling.LANCZOS)
                self.img_fondo = ImageTk.PhotoImage(img_res)
                self.canvas.create_image(0, 0, image=self.img_fondo, anchor="nw")
            except Exception as e:
                print(f"Error cargando el fondo: {e}")
                self.canvas.configure(bg="#1b5e20")
        else:
            self.canvas.configure(bg="#1b5e20")

        # Mazo visual
        img_reverso = self.obtener_imagen_carta("reverso")
        if img_reverso:
            self.canvas.create_image(390, 45, image=img_reverso, anchor="center")

        # Textos
        self.txt_cpu = self.canvas.create_text(
            220, 25, text="Crupier: ?", font=("Arial", 12, "bold"), fill="white"
        )
        self.txt_jugador = self.canvas.create_text(
            220, 160, text="Jugador: ?", font=("Arial", 12, "bold"), fill="white"
        )

        # Botones
        self.btn_pedir = tk.Button(
            self.canvas, text="Pedir Carta", font=("Arial", 10, "bold"), width=12,
            bg="#2196F3", fg="white", command=self.pedir_carta, bd=2
        )
        self.btn_plantar = tk.Button(
            self.canvas, text="Plantarse", font=("Arial", 10, "bold"), width=12,
            bg="#FF9800", fg="white", command=self.plantarse, bd=2
        )

        self.canvas.create_window(155, 335, window=self.btn_pedir, anchor="center")
        self.canvas.create_window(285, 335, window=self.btn_plantar, anchor="center")

    def deshabilitar_botones(self):
        self.btn_pedir.config(state="disabled")
        self.btn_plantar.config(state="disabled")

    def habilitar_botones(self):
        self.btn_pedir.config(state="normal")
        self.btn_plantar.config(state="normal")

    def actualizar_pantalla(self, mostrar_cpu_completo=False):
        for item in self.items_cartas_canvas:
            self.canvas.delete(item)
        self.items_cartas_canvas.clear()

        if mostrar_cpu_completo:
            pts_cpu = self.calcular_puntos(self.mano_cpu)
            self.canvas.itemconfig(self.txt_cpu, text=f"Crupier (Total: {pts_cpu})")
            cartas_cpu_a_mostrar = self.mano_cpu
        else:
            self.canvas.itemconfig(self.txt_cpu, text="Crupier (Total: ?)")
            cartas_cpu_a_mostrar = []
            if self.mano_cpu:
                cartas_cpu_a_mostrar.append(self.mano_cpu[0])
                if len(self.mano_cpu) > 1:
                    cartas_cpu_a_mostrar.append("reverso")

        if cartas_cpu_a_mostrar:
            n = len(cartas_cpu_a_mostrar)
            ancho_paso = 48
            x_inicio = 220 - ((n - 1) * ancho_paso) / 2
            for i, cve in enumerate(cartas_cpu_a_mostrar):
                img = self.obtener_imagen_carta(cve)
                if img:
                    item = self.canvas.create_image(x_inicio + i * ancho_paso, 85, image=img, anchor="center")
                    self.items_cartas_canvas.append(item)

        pts_jugador = self.calcular_puntos(self.mano_jugador)
        self.canvas.itemconfig(self.txt_jugador, text=f"Tu mano (Total: {pts_jugador})")

        if self.mano_jugador:
            n = len(self.mano_jugador)
            ancho_paso = 48
            x_inicio = 220 - ((n - 1) * ancho_paso) / 2
            for i, cve in enumerate(self.mano_jugador):
                img = self.obtener_imagen_carta(cve)
                if img:
                    item = self.canvas.create_image(x_inicio + i * ancho_paso, 220, image=img, anchor="center")
                    self.items_cartas_canvas.append(item)

    def animar_desplazamiento_carta(self, valor_carta, y_destino, num_cartas_destino, callback_al_terminar, es_reverso=False):
        x_inicio, y_inicio = 390, 45
        
        n = num_cartas_destino + 1
        ancho_paso = 48
        x_fin = (220 - ((n - 1) * ancho_paso) / 2) + (num_cartas_destino * ancho_paso)

        cve = "reverso" if es_reverso else valor_carta
        img = self.obtener_imagen_carta(cve)

        if img:
            item_flotante = self.canvas.create_image(x_inicio, y_inicio, image=img, anchor="center")
        else:
            item_flotante = self.canvas.create_text(x_inicio, y_inicio, text=cve, fill="white", font=("Arial", 12, "bold"))

        pasos = 10
        dx = (x_fin - x_inicio) / pasos
        dy = (y_destino - y_inicio) / pasos

        def paso_animacion(i):
            if i <= pasos:
                self.canvas.coords(item_flotante, x_inicio + dx * i, y_inicio + dy * i)
                self.after(18, lambda: paso_animacion(i + 1))
            else:
                self.canvas.delete(item_flotante)
                callback_al_terminar()

        paso_animacion(1)

    def iniciar_reparto_inicial(self):
        # Reproducir sonido de mezcla/reparto al inicio de la ronda
        self.reproducir_sfx("Dealing-cards-sound.mp3")

        c1_jug = self.sacar_carta()
        c1_cpu = self.sacar_carta()
        c2_jug = self.sacar_carta()
        c2_cpu = self.sacar_carta()

        def fin_reparto():
            self.mano_cpu.append(c2_cpu)
            self.actualizar_pantalla(mostrar_cpu_completo=False)
            if self.calcular_puntos(self.mano_jugador) == 21:
                self.after(1000, self.plantarse)
            else:
                self.habilitar_botones()

        def paso4():
            self.mano_jugador.append(c2_jug)
            self.actualizar_pantalla(mostrar_cpu_completo=False)
            self.animar_desplazamiento_carta("reverso", 85, 1, fin_reparto, es_reverso=True)

        def paso3():
            self.mano_cpu.append(c1_cpu)
            self.actualizar_pantalla(mostrar_cpu_completo=False)
            self.animar_desplazamiento_carta(c2_jug, 220, 1, paso4)

        def paso2():
            self.mano_jugador.append(c1_jug)
            self.actualizar_pantalla(mostrar_cpu_completo=False)
            self.animar_desplazamiento_carta(c1_cpu, 85, 0, paso3)

        self.animar_desplazamiento_carta(c1_jug, 220, 0, paso2)

    def pedir_carta(self):
        self.deshabilitar_botones()
        c = self.sacar_carta()
        num_cartas_actual = len(self.mano_jugador)

        def al_terminar_animacion():
            self.mano_jugador.append(c)
            self.actualizar_pantalla()
            if self.calcular_puntos(self.mano_jugador) > 21:
                self.after(1200, lambda: self.perder("¡Te pasaste de 21!"))
            else:
                self.habilitar_botones()

        self.animar_desplazamiento_carta(c, 220, num_cartas_actual, al_terminar_animacion)

    def plantarse(self):
        self.deshabilitar_botones()
        self.actualizar_pantalla(mostrar_cpu_completo=True)
        self.after(800, self.evaluar_o_pedir_cpu)

    def evaluar_o_pedir_cpu(self):
        if self.calcular_puntos(self.mano_cpu) < 17:
            c = self.sacar_carta()
            num_cartas_actual = len(self.mano_cpu)

            def al_terminar():
                self.mano_cpu.append(c)
                self.actualizar_pantalla(mostrar_cpu_completo=True)
                self.after(500, self.evaluar_o_pedir_cpu)

            self.animar_desplazamiento_carta(c, 85, num_cartas_actual, al_terminar)
        else:
            self.after(1200, self.evaluar_ganador)

    def evaluar_ganador(self):
        pts_jugador = self.calcular_puntos(self.mano_jugador)
        pts_cpu = self.calcular_puntos(self.mano_cpu)

        if pts_cpu > 21:
            self.ganar("¡El crupier se pasó de 21!")
        elif pts_jugador > pts_cpu:
            self.ganar(f"¡Ganaste! {pts_jugador} supera a {pts_cpu} del crupier.")
        elif pts_jugador < pts_cpu:
            self.perder(f"El crupier te superó ({pts_cpu} vs {pts_jugador}).")
        else:
            self.perder(f"Empate ({pts_jugador} a {pts_cpu}). La casa gana.")

    def ganar(self, mensaje):
        self.detener_musica()
        self.reproducir_sfx("ganaste.mp3")
        messagebox.showinfo("¡Victoria!", f"{mensaje}\n\nRevelando resultado...")
        self.destroy()
        self.al_ganar_callback()

    def perder(self, mensaje="Has perdido."):
        self.detener_musica()
        self.reproducir_sfx("perdiste negro.mp3")
        messagebox.showerror("Derrota", f"{mensaje}\n\nCerrando aplicación sin guardar...")
        self.parent.destroy()
        sys.exit()