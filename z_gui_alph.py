import tkinter as tk
from tkinter import filedialog, Text, ttk
from PIL import Image, ImageTk
import os
import subprocess

#Iniciamos la lista con una letra vacía, para no generar problemas
letra = ""

#posteriormente, cargamos el archivo de texto en modo lectura de Labels, el cual contiene nuestros registros de letras guardadas
#y obtenemos el tercer registro, omitiendo el indice y su espacio, y la vamos guardando en una variable global.
def func_mostrar_tercer_caracter():
    global letra
    archivo_texto = 'Modelo/labels.txt'
    try:
        with open(archivo_texto, 'r') as file: 
            renglones = file.readlines()
            caracteres = [renglon[2] for renglon in renglones if len(renglon) > 2]
            combo_renglones['values'] = caracteres
    except FileNotFoundError:
        combo_renglones['values'] = ["El archivo 'labels.txt' no se encontró."]

#Mandamos a llamar la imagen con la letra que seleccionamos en el checkbox, en la ubicación donde se encuentran las imagenes
def func_mostrar_imagen(seleccion_letra):
    ruta_imagen = f'Datos/Train/{seleccion_letra}/Image_0.jpg'
    if os.path.exists(ruta_imagen):
        imagen = Image.open(ruta_imagen)
        imagen = imagen.resize((250, 250), Image.LANCZOS)
        imagen_tk = ImageTk.PhotoImage(imagen)
        etiqueta_imagen.config(image=imagen_tk)
        etiqueta_imagen.image = imagen_tk
    else:
        etiqueta_imagen.config(text="Imagen no encontrada", image='')

#Seleccionamos la letra desde el combobox y posteriormente mandamos a llamar la funcion de mostrar imagen con la letra seleccionada
def func_seleccionar_letra(event):
    global letra
    letra = combo_renglones.get()
    func_mostrar_imagen(letra)

#Regresamos a la interfaz
def func_enviar_a_interfaz():
    root.destroy()  
    subprocess.Popen(["python", "z_gui_interfaz.py"])

def crear_boton(root, text, command, x, y, bg='white', fg='#562155', width=15, height=2, font=('Comfortaa', 12, 'bold')):
    boton = tk.Button(root, text=text, bg=bg, fg=fg, width=width, height=height, 
                      borderwidth=0, relief="flat", font=font, command=command)
    boton.place(x=x, y=y)
    return boton

root = tk.Tk()
root.title("Alfabeto")
root.geometry("640x400")
root.configure(bg='#8e8ca3')
root.resizable(False, False)

combo_renglones = ttk.Combobox(root, width=50)
combo_renglones.place(x=20, y=20)
combo_renglones.bind("<<ComboboxSelected>>", func_seleccionar_letra)

etiqueta_imagen = tk.Label(root, bg='#8e8ca3')
etiqueta_imagen.place(x=350, y=60)

crear_boton(root, "Regresar", func_enviar_a_interfaz, 20, 100)

# Cargar automáticamente los caracteres al iniciar
func_mostrar_tercer_caracter()

root.mainloop()
