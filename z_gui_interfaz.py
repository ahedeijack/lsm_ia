import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox
import os
import subprocess
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import cv2
from PIL import Image, ImageTk
import numpy as np
import math
import time
import difflib


#Mejora de calidad de captura
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Aumenta la resolución
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

root = tk.Tk()
root.title("Interfaz")
root.geometry("1280x720")
root.configure(bg='#8e8ca3')

#Crear una etiqueta para mostrar la imagen capturada de la cámara
imagen_label = tk.Label(root)
imagen_label.place(x=0, y=0, relwidth=1, relheight=1)  #Estira la imagen para cubrir toda la ventana

# Crear un slider para ajustar el porcentaje de similitud
similarity_slider = tk.Scale(root, from_=1, to=100, orient='horizontal', label="Similitud (%)", bg='#8e8ca3')
similarity_slider.place(x=120, y=300)
similarity_slider.set(60)  # Valor inicial en 60%

#Configuración de los botones
def func_conf():
    root.destroy()
    subprocess.Popen(["python", "z_gui_conf.py"])

#En caso de que se encuentre un error, se guarda la palabra que tuvo el error
#además de guardar su palabra corregida. Así mismo, guarda tambien 
#en el diccionario interno, la palabra corregida.
def guardar_correccion(palabra, correccion):
    with open("Datos/Analisis/z_correciones.txt", "a") as f:
        f.write(f"'{palabra}' : '{correccion}'\n")
    with open("Datos/Analisis/z_info_diccionario.txt", "a") as ft:
        ft.write(f"{correccion}\n")

#Abre la función para abrir las capturas.
def func_captures():
    root.destroy()
    subprocess.Popen(["python", "z_gui_captura.py"])

#Aquí se guarda la frecuencia con la que las letras son detectadas. 
#Abre el archivo y agrega la letra detectada junto a un salto de línea.
def guardar_en_frecuencias(texto, archivo="Datos/Analisis/z_frecuencias.txt"):
    with open(archivo, "a") as f:  
        f.write(texto + "\n")  

#Para corroborar la precisión, se guarda el resultado correcto o incorrecto de manera binaria
#en un archivo de texto
def guardar_en_binario(resultado, archivo="Datos/Analisis/z_binarios.txt"):
    with open(archivo, "a") as f:
        f.write(f"{resultado}\n")

#Abre la configuración para ver nuestro alfabeto.
def func_alph():
    root.destroy()
    subprocess.Popen(["python", "z_gui_alph.py"])

#Función para generar botones de manera rapida y otpima 
def crear_boton(root, text, command, x, y, bg='white', fg='#562155', width=15, height=2, font=('Comfortaa', 12, 'bold')):
    boton = tk.Button(root, text=text, bg=bg, fg=fg, width=width, height=height, 
                      borderwidth=0, relief="flat", font=font, command=command)
    boton.place(x=x, y=y)
    return boton

#Cuando se detecta un error, también se almacena la palabra que tuvo el error para poder analizarla más adelante.
def guardar_error(palabra):
    with open("Datos/Analisis/z_errores.txt", "a") as f:
        f.write(f"{palabra}\n")

#Al finalizar la captura, mostramos una ventana en la que en caso de que la palabra sea la correcta, se llama a la función
#que guarda el archivo en binario, y en caso contrario, se mandan a llamar a las funciones para guardar en binario, 
#guardar el error y la palabra, así como la correción de la palabra. 
def mostrar_ventana_confirmacion(palabra_detectada):
    respuesta = messagebox.askquestion("Confirmación", f"¿La detección de '{palabra_detectada}' fue correcta?")
    if respuesta == "yes":
        guardar_en_binario(1)
    else:
        guardar_en_binario(0)
        guardar_error(palabra_detectada)
        corregir_palabra(palabra_detectada)
    global registro
    registro = ""

#En esta función, cargamos nuestro diccionario interno para empezar a hacer las comparaciones en tiempo real.
def cargar_diccionario(archivo):
    with open(archivo, 'r') as f:
        return [line.strip() for line in f]

# en esta función mandamos a llamar 3 parametros: 
# 'Palabra' La cual es la palabra detectada, y en caso de tener espacios, los elimina
# 'Diccionario' El cual es el que tenemos registrado
# 'Porcentaje de similitud' Que es un valor que comparará la palabra detectada contra la palabra más similar en el diccionario
def obtener_sugerencias(palabra, diccionario, porcentaje_similitud):
    palabra_sin_espacios = palabra.replace(" ", "")
    similitud = porcentaje_similitud / 100  # Convertir el porcentaje a decimal

    #Generamos un arreglo el cual se llenara con las palabras que hay en nuestro diccionario
    sugerencias = []
    for palabra_diccionario in diccionario:
        # Posteriormente va a comparar la palabra detectada 
        ratio = difflib.SequenceMatcher(None, palabra_sin_espacios, palabra_diccionario).ratio()
        if ratio >= similitud:
            sugerencias.append(palabra_diccionario)
    
    return sugerencias

#Palabra imnicial 
indice_actual = 0 
#Maximo de sugerencias 
max_sugerencias = 5
sugerencias = []  


# Modificar la función para mostrar solo un máximo de 5 sugerencias y resaltar según el índice
#Se empiezan a mostrar la sugerencias pero solo de 5 en 5 
def mostrar_sugerencias(label, sugerencias):
    global indice_actual
    #Se muestran las sugerencias obtenidas y se almacenan
    max_display_suggestions = min(len(sugerencias), max_sugerencias)  # Máximo de sugerencias visibles
    texto = ""
    
    # Muestra las sugerencias según el indice, el cual comienza en 0 siendo la prmera
    for i in range(max_display_suggestions):
        if i == indice_actual:
            texto += f"-> {sugerencias[i]} "  
        else:
            texto += f"{sugerencias[i]} "
        if i < max_display_suggestions - 1:
            texto += " | " 
        #Se iran separando según sea la palabra 

    #Se genera la configuración de los subtitulos 
    label.config(text=texto, bg='black', fg='white', font=('Helvetica', 18, 'bold'))
    label.place(relx=0.5, rely=0.8, anchor='center')  # Ajustar la ubicación de las sugerencias

#Cuano la palabra se ha obtenido en la lista, se selecciona la primera
def resaltar_siguiente(sugerencias):
    global indice_actual
    max_display_suggestions = min(len(sugerencias), max_sugerencias)
    
    #Pasa por las sugerencias siempre y cuando halla más de 0
    if max_display_suggestions > 0:
        #Y en caso de llegar al final, se regresa al inicio 
        indice_actual = (indice_actual + 1) % max_display_suggestions
        mostrar_sugerencias(sugerencias_label, sugerencias)

#cuando la palabra es adecuada dentro de las sugerencias
def seleccionar_palabra(sugerencias):
    global indice_actual
    if sugerencias:
        palabra_seleccionada = sugerencias[indice_actual]
        

        #Se manda a llamar la ventana de confirmación con la palabra
        #seleccionada para posteriormente guardarla
        mostrar_ventana_confirmacion(palabra_seleccionada)

#Se corrige la palabra en caso de que la detección sea erronea
def corregir_palabra(palabra_detectada):
    #Se genera una variable con la cual se pasara a corregir la palabra 
    #en donde posteriormente se llama a la función de guardar correción
    #en donde se almacenara la palabra erronea, y la palabra corregida
    correccion = simpledialog.askstring("Corrección", f"Ingrese la corrección para '{palabra_detectada}':")
    if correccion:
        (registro, correccion)
        
#Se carga nuestro diccionario par auisarlo más adelante y se inicializa 
#el registro de manos en un valor vacio
diccionario = cargar_diccionario("Datos/Analisis/z_info_diccionario.txt")
registro = ""

#Se iran actualizando los subtitulos, agregando el nuevo texto
#a un registro, el cual sera utilizado para generar la palabra
#así mismo, si llega a más de 15, se va eliminando el texto
def actualizar_subtitulos(label, texto):
    global registro
    registro += texto

    if len(registro) > 15:
        registro = registro[-15:]
    
    label.config(text=registro, bg='black', fg='white', font=('Helvetica', 24, 'bold'))  
    label.place(relx=0.5, rely=0.9, anchor='center')

    guardar_en_frecuencias(texto)

last_update_time = time.time()

#en caso de que la detección este siendo erronea, se puede reiniciar con la siguiente funcion 
def func_reiniciar_deteccion():
    global detection_active, registro
    detection_active = True
    registro = ""
    subtitulo_label.config(text="")

#Tiempo de espera entre capturas para evitar registros repetitivos
tiempo_espera_post_captura = 2  # Tiempo de espera en segundos cuando se hace una captura
gesto_actual = ""
tiempo_inicio_gesto = 0
capturado = False                #En caso de que se halla generado la captura, se utiliza como bandera esta variable

# Variables para los tiempos de espera
tiempo_espera_siguiente = 1     #Cuando se identifica el valor de 'Siguiente' es lo que esperara en hacer una selección
tiempo_espera_seleccionar = 1   #Cuando se identifica el gesto de 'Seleccionar' tiene que esperarse un segundo para finalizar 
tiempo_espera_gestos = 2        # Tiempo de espera general para otros gestos

#Se hace uso de de los gestos Siguiente y seleccionar 
def actualizar_imagen():
    global last_update_time, gesto_actual, tiempo_inicio_gesto, capturado, sugerencias
    global gesto_siguiente_inicio, gesto_seleccionar_inicio

    success, img = cap.read()
    if success:
        imgOutput = img.copy()
        hands, img = detector.findHands(img)

        texto_detectado = ""

        #En caso de que se encuentre una mano, continua a realizar en analisis
        if hands:
            try:
                hand = hands[0] #Cantidad de gestos que se reconoceran así como sus coordenadas
                x, y, w, h = hand['bbox']

                #Posteriormente calcula y recorta la región necesaria para analizar la mano
                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                imgCrop = img[y - offset: y + h + offset, x - offset: x + w + offset]

                #Obtiene la relación de la mano con su altura(h) y su anchura(w) 
                aspectRatio = h / w

                #Se adapta la mano recortada para que se ajuste a la imagen recortada anteriormente y ser analizada 
                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    wGap = math.ceil((imgSize - wCal) / 2)
                    imgWhite[:, wGap: wCal + wGap] = imgResize
                else:
                    k = imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    hGap = math.ceil((imgSize - hCal) / 2)
                    imgWhite[hGap: hCal + hGap, :] = imgResize

                #Posteriormente, se reescala la imagen para poder oibtener su etiqueta en base a su clasificación
                imgWhite = cv2.resize(imgWhite, (224, 224))
                
                #Se obtiene la imagen predicción junto a su etiqueta y posteriormente se almacena en el arreglo de 'texto detectado' 
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
                texto_detectado = labels[index]

                #Posteriormente, se guarda el texto en el cuadrado al rededor de la mano y se muestra
                cv2.putText(imgOutput, labels[index], (x, y + h + 30), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 2)
                cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (255, 0, 255), 4)

            except Exception as e:
                print(f"Error: {e}")

        current_time = time.time()

        # Entra en uso los gestos de siguiente y seleccionar, que al momento de detectar los gestos, realiza sus tareas correspondientes 
        if texto_detectado == "Siguiente":
            if gesto_siguiente_inicio is None:
                gesto_siguiente_inicio = current_time  #En caso de que no se detecte el gesto siguiente, re reiniciar el temporizador
            elif current_time - gesto_siguiente_inicio >= tiempo_espera_siguiente: 
                resaltar_siguiente(sugerencias)  #En caso de que el tiempo se cumpla, se hace resaltar la siguiente palabra
                gesto_siguiente_inicio = None  #Posteriormente se reiniciar el temporizador 
        else:
            gesto_siguiente_inicio = None  #Y finalmente, en caso de que el codigo no se mantenga por el tiempo definido, se reinicia

        #Para la palabra de seleccionar se realiza la misma acción de iniviar el temporizador
        if texto_detectado == "Seleccionar":
            if gesto_seleccionar_inicio is None:
                gesto_seleccionar_inicio = current_time  
            elif current_time - gesto_seleccionar_inicio >= tiempo_espera_seleccionar:  
                seleccionar_palabra(sugerencias) #Pero en caso de que si se identifique seleccionar, se manda a llamar la funcion de selccionar junto con la palabra detectada 
                gesto_seleccionar_inicio = None  #Y se reiniciar el temporizador 
        else:
            gesto_seleccionar_inicio = None  # Y en caso de que no se mantenga, se reinicia nuevamente 

        # En aso de que los textos o gestos sean Siguiente o Seleccionar, se eliminan de los subtitulos detectados 
        if texto_detectado not in ["Siguiente", "Seleccionar"]:
            # Para ello pregunta si el texto detectado (que contiene Siguiente y Seleccionar) es igual al gesto
            #dentro del arreglo y no al capturado, no se agrega
            if texto_detectado == gesto_actual and not capturado:
                if current_time - tiempo_inicio_gesto >= tiempo_espera_gestos:
                    actualizar_subtitulos(subtitulo_label, texto_detectado)
                    porcentaje_similitud = similarity_slider.get()
                    sugerencias = obtener_sugerencias(registro, diccionario, porcentaje_similitud)
                    mostrar_sugerencias(sugerencias_label, sugerencias)

                    capturado = True
                    last_update_time = current_time
            else:
                #En caso contrario, se reinicia el temporizador
                gesto_actual = texto_detectado
                tiempo_inicio_gesto = current_time
                capturado = False
        #Si hay una captura y el tiempo de espera ya paso, se reinicia la captura 
        if capturado and current_time - last_update_time >= tiempo_espera_post_captura:
            capturado = False

        #convierte la imagen de BGR a RGB 
        imgRGB = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2RGB)
        imgPIL = Image.fromarray(imgRGB)
        #Posteriormente sea justa la imagen al tamño de la ventana principal
        imgPIL = imgPIL.resize((root.winfo_width(), root.winfo_height()))
        imgTK = ImageTk.PhotoImage(imgPIL)
        #Finalmente se actualiza la etiqueta de la imagen con la nueva imagen
        imagen_label.config(image=imgTK)
        imagen_label.image = imgTK

    #Se acutaliza la imagen cada 10ms 
    root.after(10, actualizar_imagen)

#Ubicaciones del modelo y sus etiquetas 
model_path = "Modelo/modelo_gestos_mejorado.h5"
labels_path = "Modelo/labels.txt"

if not os.path.exists(model_path):
    messagebox.showerror("Error", "El archivo del modelo no se encuentra.")
    func_captures()
    root.destroy()
elif not os.path.exists(model_path):
    messagebox.showerror("Error", "Las etiquedas del modelo no se encuentra.")
    func_captures()
    root.destroy()
else:
    cap = cv2.VideoCapture(0)
    detector = HandDetector(maxHands=1)
    classifier = Classifier(model_path, labels_path)

    offset = 20
    imgSize = 100

    def cargar_etiquetas(ruta):
        etiquetas = {}
        with open(ruta, 'r') as f:
            for line in f:
                index, label = line.strip().split()
                etiquetas[int(index)] = label
        return etiquetas

    labels = cargar_etiquetas(labels_path)

    subtitulo_label = tk.Label(root, text="", font=('Helvetica', 24, 'bold'))
    sugerencias_label = tk.Label(root, text="", font=('Helvetica', 18, 'bold'))
    
    actualizar_imagen()

xBtn = 100
crear_boton(root, text="Configuración",         command=func_conf,                              x=xBtn, y=60)
crear_boton(root, text="Alfabeto",              command=func_alph,                              x=xBtn, y=120)
crear_boton(root, text="Captura",               command=func_captures,                          x=xBtn, y=180)
crear_boton(root, text="Reiniciar detección",   command=func_reiniciar_deteccion,               x=xBtn, y=240)

root.mainloop()

cap.release()
cv2.destroyAllWindows()
