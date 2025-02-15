import matplotlib.pyplot as plt
from collections import Counter
import difflib
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess  # Para abrir z_gui_conf.py

# Funciones para leer archivos y procesar datos
def func_leer_archivo_binarios(archivo="Datos/Analisis/z_binarios.txt"):
    #De nuestro arhcivo z_binarios. vamos a obtener nuestros aciertos y fallos
    with open(archivo, "r") as f:
        lineas = f.read().splitlines()
    valores = [int(linea) for linea in lineas if linea.strip()]
    return Counter(valores)

def func_leer_archivo_frecuencias(archivo="Datos/Analisis/z_frecuencias.txt"):
   #Del archivo de frecuencias, vamos a leer cada que una letra aparezca
    with open(archivo, "r") as f:
        lineas = f.read().splitlines()
    etiquetas = [linea for linea in lineas if linea.strip()]
    return Counter(etiquetas)

def func_leer_archivo_correcciones(archivo="Datos/Analisis/z_correciones.txt"):
    #Del archivo de Z_Correciones vamos a comparar la palabra que se escribiio correctamente
    #con la que se escribiio incorrectamente
    with open(archivo, "r") as f:
        lineas = f.read().splitlines()

    pares_palabras = []
    for linea in lineas:
        if " : " in linea:
            incorrecta, corregida = linea.split(" : ")
            incorrecta = incorrecta.strip("' ").strip()
            corregida = corregida.strip("' ").strip()
            pares_palabras.append((incorrecta, corregida)) 
    return pares_palabras

#Función para graficar los errores y aciertos con los valores encontrador en los aciertos y fallos 
def func_graficar_pastel(frecuencias):
    labels = ['Fallos (0)', 'Aciertos (1)']
    sizes = [frecuencias[0], frecuencias[1]]
    colors = ['lightcoral', 'lightgreen']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.savefig("Datos/Analisis/grafica_pastel.png")
    return fig

#Creamos una grafica de pasterl con las freciemtas de las letras que han aparecido
def func_graficar_frecuencias(frecuencias):
    etiquetas = list(frecuencias.keys())
    conteo = list(frecuencias.values())
    
    fig, ax = plt.subplots()
    ax.bar(etiquetas, conteo, color='skyblue')
    ax.set_xlabel('Etiquetas')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Frecuencia de Etiquetas Detectadas')
    plt.savefig("Datos/Analisis/grafica_frecuencias.png")
    return fig

#Funcion para comparar las palabras con el porcentaje de correcion vs la palabra original
def func_comparar_palabras_con_porcentaje(original, corregida):
    d = difflib.ndiff(original, corregida)
    diferencias = list(d)
    errores = sum(1 for diff in diferencias if diff.startswith('-') or diff.startswith('+'))
    porcentaje_error = (errores / max(len(original), len(corregida))) * 100
    return diferencias, porcentaje_error

#Ffuncion que integra el porcentaje de las palbras corregidas y genera una grafica de barras 
#con las correcciones realizadas.
def func_graficar_comparacion_palabras(pares_palabras):
    if not pares_palabras:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No hay correcciones para mostrar", fontsize=8, ha='center')
        ax.axis('off')
        return fig

    fig, axes = plt.subplots(len(pares_palabras), 1, figsize=(10, 2 * len(pares_palabras)))
    
    if len(pares_palabras) == 1:
        axes = [axes]
    
    for i, (original, corregida) in enumerate(pares_palabras):
        diferencias, porcentaje_error = func_comparar_palabras_con_porcentaje(original, corregida)
        letras = []
        colores = []
        
        for diff in diferencias:
            if diff.startswith(' '):
                letras.append(diff[2])
                colores.append('green')
            elif diff.startswith('-'):
                letras.append(diff[2])
                colores.append('red')
            elif diff.startswith('+'):
                letras.append(diff[2])
                colores.append('blue')
        
        axes[i].bar(range(len(letras)), [1] * len(letras), color=colores, tick_label=letras)
        axes[i].set_ylim(0, 1)
        axes[i].set_yticks([])
        axes[i].set_title(f"Comparación: '{original}' vs '{corregida}' - Error: {porcentaje_error:.2f}%")

    fig.tight_layout()
    plt.savefig("Datos/Analisis/grafica_comparacion.png")
    return fig

#Mostramos las graficas en un canva 
def func_mostrar_grafica(canvas, figure):
    canvas.get_tk_widget().pack_forget()
    canvas = FigureCanvasTkAgg(figure, master=canvas.get_tk_widget().master)
    canvas.draw()
    canvas.get_tk_widget().pack()
    return canvas

#Generamos una clase para mostrar todas las graficas 
class InterfazGraficas:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualización de Gráficas")

        #Leemos los datos de donde se obtendran las grficas 
        self.frecuencias_binarios = func_leer_archivo_binarios("Datos/Analisis/z_binarios.txt")
        self.frecuencias_etiquetas = func_leer_archivo_frecuencias("Datos/Analisis/z_frecuencias.txt")
        self.pares_palabras = func_leer_archivo_correcciones("Datos/Analisis/z_correciones.txt")

        #mostramos la lista de gráficos
        self.graficas = [
            func_graficar_pastel(self.frecuencias_binarios),
            func_graficar_frecuencias(self.frecuencias_etiquetas),
            func_graficar_comparacion_palabras(self.pares_palabras)
        ]
        self.grafica_actual = 0

        #Creamos el canva donde se van a mostrar las graficas 
        self.canvas = FigureCanvasTkAgg(self.graficas[self.grafica_actual], master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        instrucciones = tk.Label(self.root, text="Usa las flechas del teclado para cambiar de gráfica.")
        instrucciones.pack(pady=10)
        self.root.bind("<Right>", self.func_siguiente_grafica_event)
        self.root.bind("<Left>", self.func_anterior_grafica_event)
        self.func_crear_botones()

    def func_crear_botones(self):
        frame_botones = ttk.Frame(self.root)
        frame_botones.pack(pady=10)

        boton_anterior = ttk.Button(frame_botones, text="Anterior", command=self.func_anterior_grafica)
        boton_anterior.pack(side=tk.LEFT, padx=5)

        boton_volver = ttk.Button(frame_botones, text="Volver", command=self.func_volver_a_config)
        boton_volver.pack(side=tk.LEFT, padx=5)

        boton_siguiente = ttk.Button(frame_botones, text="Siguiente", command=self.func_siguiente_grafica)
        boton_siguiente.pack(side=tk.LEFT, padx=5)

    def func_siguiente_grafica(self):
        self.grafica_actual = (self.grafica_actual + 1) % len(self.graficas)
        self.func_actualizar_grafica()

    def func_anterior_grafica(self):
        self.grafica_actual = (self.grafica_actual - 1) % len(self.graficas)
        self.func_actualizar_grafica()

    def func_siguiente_grafica_event(self, event):
        self.func_siguiente_grafica()

    def func_anterior_grafica_event(self, event):
        self.func_anterior_grafica()

    def func_actualizar_grafica(self):
        self.canvas = func_mostrar_grafica(self.canvas, self.graficas[self.grafica_actual])

    def func_volver_a_config(self):
        self.root.destroy()
        subprocess.Popen(["python", "z_gui_conf.py"])

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGraficas(root)
    root.mainloop()
