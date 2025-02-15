import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import os
import shutil  # Para eliminar archivos
import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox
import subprocess

def func_detectar_camaras():
    """Detecta las cámaras disponibles en el sistema y las devuelve en una lista."""
    camaras_disponibles = []
    for i in range(10):  # Probar hasta 10 índices de cámara
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            camaras_disponibles.append(f"Cámara {i}")
            cap.release()
    return camaras_disponibles

def func_seleccionar_camara():
    """Muestra una ventana con un Listbox para seleccionar una cámara disponible."""
    def seleccionar():
        global cam_index
        seleccion = listbox.curselection()
        if seleccion:
            cam_index = int(listbox.get(seleccion).split(" ")[1])
            root.destroy()
    
    camaras = func_detectar_camaras()
    root = tk.Tk()
    root.title("Seleccionar Cámara")
    
    listbox = Listbox(root)
    for camara in camaras:
        listbox.insert(tk.END, camara)
    listbox.pack()
    
    boton_seleccionar = tk.Button(root, text="Seleccionar", command=seleccionar)
    boton_seleccionar.pack()
    
    root.mainloop()
    
    return cam_index if 'cam_index' in globals() else 0

# Variables globales
cap = cv2.VideoCapture(func_seleccionar_camara())
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300
folder = ""
counter = 0
imgWhite = None

def func_create_folder():
    global folder, counter
    folder_name = entry.get()
    
    if folder_name:
        folder = f"Datos/train/{folder_name}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        print(f"Directorio creado: {folder}")
        counter = 0
        label.config(text=f"Directorio actual: {folder_name}")
    else:
        label.config(text="Por favor ingresa un nombre válido.")

def func_take_capture():
    global counter, imgWhite
    if imgWhite is not None and folder:
        cv2.imwrite(f'{folder}/Image_{counter}.jpg', imgWhite)
        print(f'Imagen guardada: {folder}/Image_{counter}.jpg')
        counter += 1
    else:
        print("No se puede guardar la imagen. Asegúrese de que haya una mano detectada y que se haya creado un directorio.")

def func_delete_all():
    train_folder = "Datos/train"
    validation_folder = "Datos/validation"

    if os.path.exists("Datos"):
        respuesta = messagebox.askyesno("Confirmación", "¿Está seguro de que desea eliminar todos los archivos en 'train' y 'validation'?")
        if respuesta:
            if os.path.exists(train_folder):
                shutil.rmtree(train_folder)
                os.makedirs(train_folder)
                print("Todos los archivos en la carpeta 'train' han sido eliminados.")
            else:
                print("La carpeta 'train' no existe.")

            if os.path.exists(validation_folder):
                shutil.rmtree(validation_folder)
                os.makedirs(validation_folder)
                print("Todos los archivos en la carpeta 'validation' han sido eliminados.")
            else:
                print("La carpeta 'validation' no existe.")
        else:
            print("Eliminación cancelada.")
    else:
        print("La carpeta 'Datos' no existe.")

def func_regresar():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()
    subprocess.run(['python', 'z_gui_conf.py'])

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

    capture_button = tk.Button(root, text="Tomar Captura", command=func_take_capture)
    capture_button.pack(pady=5)

    delete_button = tk.Button(root, text="Eliminar Todo", command=func_delete_all)
    delete_button.pack(pady=5)

    regresar_button = tk.Button(root, text="Regresar", command=func_regresar)
    regresar_button.pack(pady=5)

    root.update()

def func_hand_capture():
    global imgWhite
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)

        cv2.putText(img, "Imagenes guardadas en "+folder+": "+str(counter), 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if hands:
            try:
                hand = hands[0]
                x, y, w, h = hand['bbox']
                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                imgCrop = img[y - offset: y + h + offset, x - offset: x + w + offset]
                aspectRatio = h / w

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

            except Exception as e:
                print(f"Error: {e}")
                continue

        cv2.imshow("Image", img)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

        root.update()

if __name__ == "__main__":    
    func_setup_gui()
    func_hand_capture()

    cap.release()
    cv2.destroyAllWindows()
    root.destroy()
