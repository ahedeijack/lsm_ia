import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def entrenar_modelo():
    root.destroy()  
    subprocess.Popen(["python", "z_prcs_train.py"])## Entrenamiento del modelo  

def graficas():
    root.destroy()  
    subprocess.Popen(["python", "z_gui_graficas.py"])  

def graficas_modelo():
    root.destroy()  
    subprocess.Popen(["python", "z_gui_graficas_modelos.py"])  

def regresar():
    root.destroy()  
    subprocess.Popen(["python", "z_gui_interfaz.py"])  

def crear_boton(root, text, command, x, y, bg='white', fg='#562155', width=15, height=2, font=('Comfortaa', 12, 'bold')):
    boton = tk.Button(root, text=text, bg=bg, fg=fg, width=width, height=height, 
                      borderwidth=0, relief="flat", font=font, command=command)
    boton.place(x=x, y=y)
    return boton

root = tk.Tk()
root.title("Configuración")  
root.geometry("640x400")  
root.configure(bg='#8e8ca3')  
root.resizable(False, False)

xBtn = 214

# Crear los botones utilizando la función crear_boton
crear_boton(root, text="Entrenar Modelo",   command=entrenar_modelo,           x=xBtn, y=60)
crear_boton(root, text="Abrir graficas",    command=graficas,                  x=xBtn, y=120)
crear_boton(root, text="Gráficas (modelos)",          command=graficas_modelo,                  x=xBtn, y=180)
crear_boton(root, text="Regresar",          command=regresar,                  x=xBtn, y=240)

root.mainloop()
