"""
📚 Visor de Alfabeto de Gestos
==============================
Muestra las letras disponibles según labels.txt
y la primera imagen de cada letra en Datos/train/<letra>/Image_0.jpg
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import subprocess

# Global UI/state variables
root = tk.Tk()
root.title("Alfabeto")
root.geometry("640x400")
root.configure(bg="#8e8ca3")
root.resizable(False, False)

combo_renglones = ttk.Combobox(root, width=40, state="readonly")
combo_renglones.place(x=20, y=20)

etiqueta_imagen = tk.Label(root, bg="#8e8ca3")
etiqueta_imagen.place(x=330, y=60)

letra_actual = ""


def func_leer_letras_desde_labels(archivo: str = "Modelo/labels.txt"):
    """
    Lee labels.txt y devuelve la lista de nombres de clase.
    Formato esperado por línea: "<indice> <etiqueta>".
    """
    letras = []
    if not os.path.exists(archivo):
        return letras

    with open(archivo, "r", encoding="utf-8") as f:
        for line in f:
            partes = line.strip().split()
            if len(partes) >= 2:
                # partes[0] = índice, resto = etiqueta (por si tiene espacios)
                etiqueta = " ".join(partes[1:])
                letras.append(etiqueta)
    return letras


def func_mostrar_letras_en_combobox():
    """
    Carga las letras desde labels.txt y las coloca en el combobox.
    """
    letras = func_leer_letras_desde_labels()
    if letras:
        combo_renglones["values"] = letras
        combo_renglones.set("Selecciona una letra / gesto")
    else:
        combo_renglones["values"] = ["No se encontró 'labels.txt' o está vacío"]
        combo_renglones.set("Sin letras disponibles")


def func_mostrar_imagen(letra: str):
    """
    Muestra la imagen de ejemplo para la letra seleccionada.
    Busca en Datos/train/<letra>/Image_0.jpg (respetar mayúsculas/minúsculas).
    """
    etiqueta_imagen.config(image="", text="", compound="center")

    if not letra or letra.startswith("No se encontró") or letra.startswith("Sin letras"):
        etiqueta_imagen.config(text="Selecciona una letra válida")
        return

    # Ajusta la ruta según tu estructura real (train vs Train)
    carpeta = os.path.join("Datos", "train", letra)
    ruta_imagen = os.path.join(carpeta, "Image_0.jpg")

    if os.path.exists(ruta_imagen):
        try:
            imagen = Image.open(ruta_imagen)
            imagen = imagen.resize((250, 250), Image.LANCZOS)
            imagen_tk = ImageTk.PhotoImage(imagen)
            etiqueta_imagen.config(image=imagen_tk, text="")
            etiqueta_imagen.image = imagen_tk  # evitar que el GC la borre
        except Exception as e:
            etiqueta_imagen.config(text=f"Error al cargar imagen:\n{e}")
    else:
        etiqueta_imagen.config(
            text=f"Imagen no encontrada:\n{ruta_imagen}", image=""
        )


def func_seleccionar_letra(event=None):
    """
    Evento cuando el usuario selecciona una letra del combobox.
    """
    global letra_actual
    letra_actual = combo_renglones.get()
    func_mostrar_imagen(letra_actual)


def func_enviar_a_interfaz():
    """
    Cierra esta ventana y abre la interfaz principal.
    """
    root.destroy()
    subprocess.Popen(["python", "z_gui_interfaz.py"])


def func_crear_boton(root, text, command, x, y,
                     bg="white", fg="#562155",
                     width=15, height=2,
                     font=("Comfortaa", 12, "bold")):
    """
    Crea un botón estilizado y lo coloca en (x, y).
    """
    boton = tk.Button(root, text=text, bg=bg, fg=fg, width=width, height=height,
                      borderwidth=0, relief="flat", font=font, command=command)
    boton.place(x=x, y=y)
    return boton


# Bindings y botones
combo_renglones.bind("<<ComboboxSelected>>", func_seleccionar_letra)
func_crear_boton(root, "Regresar", func_enviar_a_interfaz, 20, 80)

# Cargar automáticamente las letras al iniciar
func_mostrar_letras_en_combobox()

root.mainloop()
