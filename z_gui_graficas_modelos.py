import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess  # Importar subprocess

# Función para leer los datos de cualquier archivo de modelo que sea recivido 
def func_leer_archivo_modelo(archivo):
    with open(archivo, "r") as f:
        lineas = f.read().splitlines()

    epocas = []
    val_loss = []
    val_acc = []

    for linea in lineas[1:]:  # Ignorar la cabecera
        datos = linea.split()
        epocas.append(int(datos[0]))
        val_loss.append(float(datos[1]))
        val_acc.append(float(datos[2]))

    return epocas, val_loss, val_acc

def func_graficar_modelo(epocas, val_loss, val_acc):
    #Según el archivo seleccionado, se genera la grafica
    fig, ax1 = plt.subplots(figsize=(10, 6))  

    ax1.set_xlabel('Época')
    ax1.set_ylabel('val_loss', color='tab:red')
    ax1.plot(epocas, val_loss, color='tab:red', label='val_loss')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax2 = ax1.twinx()  # Segundo eje y para val_acc
    ax2.set_ylabel('val_acc', color='tab:blue')
    ax2.plot(epocas, val_acc, color='tab:blue', label='val_acc')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    fig.suptitle("Evolución de val_loss y val_acc", fontsize=16)  # Título más claro

    fig.tight_layout(pad=2.0)  # Ajustar el layout para evitar el corte del título
    return fig


class InterfazGraficas:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualización de Gráficas")

        #Seleccionamos el modelo para agregar al combobox desde su ruta
        self.modelos = {
            "z_modelo_L2": "Datos/Analisis/info_modelos/z_modelo_L2.txt",
            "z_modelo_Transfer": "Datos/Analisis/info_modelos/z_modelo_Transfer.txt",
            "z_modelo_Transfer2": "Datos/Analisis/info_modelos/z_modelo_Transfer2.txt",
            "z_modelo_Dropout": "Datos/Analisis/info_modelos/z_modelo_Dropout.txt"
        }

        ##Creamos el combobox con la informacion del archivo (modelos)
        self.combobox_modelos = ttk.Combobox(self.root, values=list(self.modelos.keys()), state="readonly")
        self.combobox_modelos.current(0)  
        self.combobox_modelos.pack(pady=10)

        #Regresar 
        self.boton_regresar = tk.Button(self.root, text="Regresar", command=self.regresar)
        self.boton_regresar.pack(pady=10)

        self.combobox_modelos.bind("<<ComboboxSelected>>", self.func_actualizar_grafica)

        #Segun el archivo, mostramos el modelo y su grafica
        self.epocas, self.val_loss, self.val_acc = func_leer_archivo_modelo(self.modelos[self.combobox_modelos.get()])
        self.grafica_actual = func_graficar_modelo(self.epocas, self.val_loss, self.val_acc)

        #Generamos el Canva donde se mostrara la grafica 
        self.canvas = FigureCanvasTkAgg(self.grafica_actual, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def func_actualizar_grafica(self, event):
        #Según el modelo, se muyestra la grafica
        modelo_seleccionado = self.combobox_modelos.get()
        archivo = self.modelos[modelo_seleccionado]
        
        #Leer los datos del archivo seleccionado
        self.epocas, self.val_loss, self.val_acc = func_leer_archivo_modelo(archivo)
        
        #Se limpia el canva anteriormente generado  y semmuestra la nueva grafica en un nuevo canva
        self.canvas.get_tk_widget().pack_forget()
        nueva_figura = func_graficar_modelo(self.epocas, self.val_loss, self.val_acc)
        self.canvas = FigureCanvasTkAgg(nueva_figura, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def regresar(self):
        #Regresamos
        self.root.destroy()
        subprocess.run(["python", "z_gui_conf.py"])  

#Ejecutams nuestra aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGraficas(root)
    root.mainloop()
