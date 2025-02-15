import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import os
import shutil  # Para eliminar archivos
import tkinter as tk
from tkinter import messagebox
import subprocess

# Variables globales
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300
folder = ""
counter = 0
imgWhite = None

#Para funcionar, creamos un directorio con el nombre de nuestra ventana en tkinter
def func_create_folder():
    global folder, counter
    folder_name = entry.get()
    
    #Validamos que el nombre sea valido, y posteriormente creamos el directorio
    #Y el contador de imagenes, lo reiniciamos a 0
    if folder_name:
        folder = f"Datos/train/{folder_name}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        print(f"Directorio creado: {folder}")
        counter = 0
        label.config(text=f"Directorio actual: {folder_name}")
    else:
        label.config(text="Por favor ingresa un nombre válido.")

#Inicializamos la captura de imagenes y validamos que halla imagenes en la carpeta y el diccionario existe
#Enseguida agregamos la imagen capturada y aumentamos 1 al contador
def func_take_capture():
    global counter, imgWhite
    if imgWhite is not None and folder:
        cv2.imwrite(f'{folder}/Image_{counter}.jpg', imgWhite)  # Guarda imagen de la mano
        print(f'Imagen guardada: {folder}/Image_{counter}.jpg')
        counter += 1
    else:
        print("No se puede guardar la imagen. Asegúrese de que haya una mano detectada y que se haya creado un directorio.")

#En caso de que se seleccione eliminar, vamos a eliminar todo dentro de la carpeta Datos,
#la cual incluye las etiquetas y las carpetas con las imagenes capturadas
def func_delete_all():
    train_folder = "Datos/train"
    validation_folder = "Datos/validation"

    if os.path.exists("Datos"):
        respuesta = messagebox.askyesno("Confirmación", "¿Está seguro de que desea eliminar todos los archivos en 'train' y 'validation'?")
        if respuesta:
            # Eliminar contenido de train
            if os.path.exists(train_folder):
                shutil.rmtree(train_folder)
                os.makedirs(train_folder)  # Recrea la carpeta vacía
                print("Todos los archivos en la carpeta 'train' han sido eliminados.")
            else:
                print("La carpeta 'train' no existe.")

            # Eliminar contenido de validation
            if os.path.exists(validation_folder):
                shutil.rmtree(validation_folder)
                os.makedirs(validation_folder)  # Recrea la carpeta vacía
                print("Todos los archivos en la carpeta 'validation' han sido eliminados.")
            else:
                print("La carpeta 'validation' no existe.")
        else:
            print("Eliminación cancelada.")
    else:
        print("La carpeta 'Datos' no existe.")

#Volvemos a la configuración
def func_regresar():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()
    subprocess.run(['python', 'z_gui_conf.py'])

#Generamos nuestra interfaz de captura
def func_setup_gui():
    global root, entry, label
    root = tk.Tk()
    root.title("Gestor de Directorios")

    frame = tk.Frame(root)
    frame.pack(pady=20)

    entry_label = tk.Label(frame, text="Nombre del nuevo directorio:")
    entry_label.grid(row=0, column=0, padx=10)

    entry = tk.Entry(frame, width=30)
    entry.grid(row=0, column=1, padx=10)

    create_button = tk.Button(frame, text="Crear Directorio", command=func_create_folder)
    create_button.grid(row=1, column=0, columnspan=2, pady=10)

    label = tk.Label(root, text="No se ha creado ningún directorio.")
    label.pack(pady=10)

    #Botón para tomar captura
    capture_button = tk.Button(root, text="Tomar Captura", command=func_take_capture)
    capture_button.pack(pady=5)

    #Botón para eliminar todos los archivos
    delete_button = tk.Button(root, text="Eliminar Todo", command=func_delete_all)
    delete_button.pack(pady=5)

    #Regresar
    regresar_button = tk.Button(root, text="Regresar", command=func_regresar)
    regresar_button.pack(pady=5)

    root.update()

#Para capturar la imagen funcional, tenemos que procesarla de la siguiente manera 
def func_hand_capture():
    global imgWhite
    while True:
        #Generamos la captura en un cuadro
        success, img = cap.read()
        #Detecamos las imagenes, abajo declaramos en hand que solo sera 1 
        hands, img = detector.findHands(img)

        cv2.putText(img, "Imagenes guardadas en "+folder+": "+str(counter), 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if hands:
            try:
                hand = hands[0]
                x, y, w, h = hand['bbox'] #Obtenemos las coordenadas de las imagenes seg+un la captura 

                #Creamos una imagen en blanco la cual nos ayudara a reescalar nuestras imagenes
                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                
                #Posteirormente recortaremos la imagen que esta dentro del recuadro
                #Esto para que todas cumplan con el tamaño de imagen necesario (300*300) y halla uniformidad de información
                imgCrop = img[y - offset: y + h + offset, x - offset: x + w + offset]

                #Calcula la relación de aspecto de las imagenes
                aspectRatio = h / w

                #Si la imagen es mas alta que ancha, se genera un margen para rellenar de manera vertical
                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    wGap = math.ceil((imgSize - wCal) / 2)
                    imgWhite[:, wGap: wCal + wGap] = imgResize
                else:
                #En caso de que no, se genera el margen de manera horizontal
                    k = imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    hGap = math.ceil((imgSize - hCal) / 2)
                    imgWhite[hGap: hCal + hGap, :] = imgResize

            except Exception as e:
                print(f"Error: {e}")
                continue  #Si hay un error, solo salta de frame 

        cv2.imshow("Image", img)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

        # Actualización de la ventana de tkinter
        root.update()

# Ejecución principal
if __name__ == "__main__":    
    func_setup_gui()
    func_hand_capture()

    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

