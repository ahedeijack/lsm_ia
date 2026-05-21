"""
🤲 Enhanced Sign Language GUI Recognition System (FINAL, TUNED)
===============================================================
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
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
import logging
from pathlib import Path
from typing import List, Dict

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Config
# --------------------------------------------------
MODEL_PATH = "Modelo/mejor_modelo_gestos.h5"
LABELS_PATH = "Modelo/labels.txt"
DICT_PATH = "Datos/Analisis/z_info_diccionario.txt"

IMG_SIZE = 224
OFFSET = 20
MIN_CROP_SIZE = 20

# Timing
tiempo_espera_post_captura = 0.5
tiempo_espera_siguiente = 0.4
tiempo_espera_seleccionar = 0.4
tiempo_espera_gestos = 1.0   # ← ahora ~1 segundo

# --------------------------------------------------
# Global state
# --------------------------------------------------
cap = None
detector = None
classifier = None
labels: Dict[int, str] = {}
diccionario: List[str] = []

registro = ""
sugerencias: List[str] = []
indice_actual = 0
max_sugerencias = 5

gesto_actual = ""
tiempo_inicio_gesto = 0.0
capturado = False
last_update_time = 0.0
gesto_siguiente_inicio = None
gesto_seleccionar_inicio = None

# FPS
frame_count = 0
last_fps_time = time.time()
current_fps = 0.0

# GUI globals
root = None
imagen_label = None
subtitulo_label = None
sugerencias_label = None
similarity_slider = None
fps_label = None

# --------------------------------------------------
# Navegación y utilidades GUI
# --------------------------------------------------
def func_conf():
    root.destroy()
    subprocess.Popen(["python", "z_gui_conf.py"])


def func_captures():
    root.destroy()
    subprocess.Popen(["python", "z_gui_captura.py"])


def func_alph():
    root.destroy()
    subprocess.Popen(["python", "z_gui_alph.py"])


def func_reiniciar_deteccion():
    global registro, gesto_actual, capturado
    registro = ""
    gesto_actual = ""
    capturado = False
    if subtitulo_label:
        subtitulo_label.config(text="")
    if sugerencias_label:
        sugerencias_label.config(text="")
    logger.info("Detección reiniciada")


def func_crear_boton(root, text, command, x, y,
                     bg="white", fg="#562155",
                     width=15, height=2,
                     font=("Comfortaa", 12, "bold")):
    boton = tk.Button(root, text=text, bg=bg, fg=fg,
                      width=width, height=height,
                      borderwidth=0, relief="flat",
                      font=font, command=command)
    boton.place(x=x, y=y)
    return boton

# --------------------------------------------------
# Archivo y logging de métricas
# --------------------------------------------------
def func_guardar_en_frecuencias(texto: str,
                                archivo: str = "Datos/Analisis/z_frecuencias.txt"):
    Path(os.path.dirname(archivo) or ".").mkdir(parents=True, exist_ok=True)
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(texto + "\n")


def func_guardar_en_binario(resultado: int,
                            archivo: str = "Datos/Analisis/z_binarios.txt"):
    Path(os.path.dirname(archivo) or ".").mkdir(parents=True, exist_ok=True)
    with open(archivo, "a") as f:
        f.write(f"{resultado}\n")


def func_guardar_error(palabra: str):
    Path("Datos/Analisis").mkdir(parents=True, exist_ok=True)
    with open("Datos/Analisis/z_errores.txt", "a", encoding="utf-8") as f:
        f.write(f"{palabra}\n")


def func_guardar_correccion(palabra: str, correccion: str):
    Path("Datos/Analisis").mkdir(parents=True, exist_ok=True)
    with open("Datos/Analisis/z_correciones.txt", "a", encoding="utf-8") as f:
        f.write(f"'{palabra}' : '{correccion}'\n")
    with open(DICT_PATH, "a", encoding="utf-8") as f:
        f.write(correccion + "\n")

# --------------------------------------------------
# Diccionario y sugerencias
# --------------------------------------------------
def func_cargar_diccionario(archivo: str) -> List[str]:
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"No se encontró el diccionario: {archivo}")
        return []


def func_obtener_sugerencias(palabra: str,
                             diccionario_local: List[str],
                             porcentaje_similitud: int) -> List[str]:
    palabra_sin_espacios = palabra.replace(" ", "")
    if not palabra_sin_espacios:
        return []
    similitud_min = porcentaje_similitud / 100.0

    sugerencias_local: List[str] = []
    for palabra_dic in diccionario_local:
        ratio = difflib.SequenceMatcher(
            None, palabra_sin_espacios, palabra_dic).ratio()
        if ratio >= similitud_min:
            sugerencias_local.append(palabra_dic)

    return sugerencias_local[:max_sugerencias]


def func_mostrar_sugerencias(label, sugerencias_local: List[str]):
    global indice_actual
    max_display = min(len(sugerencias_local), max_sugerencias)
    if max_display == 0:
        label.config(text="")
        return

    texto = ""
    for i in range(max_display):
        pref = "➤ " if i == indice_actual else ""
        texto += f"{pref}{sugerencias_local[i]}"
        if i < max_display - 1:
            texto += " | "

    label.config(text=texto, bg="black", fg="white",
                 font=("Helvetica", 18, "bold"))
    label.place(relx=0.5, rely=0.8, anchor="center")


def func_resaltar_siguiente(sugerencias_local: List[str]):
    global indice_actual
    max_display = min(len(sugerencias_local), max_sugerencias)
    if max_display > 0:
        indice_actual = (indice_actual + 1) % max_display
        func_mostrar_sugerencias(sugerencias_label, sugerencias_local)


def func_seleccionar_palabra(sugerencias_local: List[str]):
    global indice_actual
    if not sugerencias_local:
        return
    palabra_seleccionada = sugerencias_local[indice_actual]
    func_mostrar_ventana_confirmacion(palabra_seleccionada)

# --------------------------------------------------
# Subtítulos y confirmación
# --------------------------------------------------
def func_actualizar_subtitulos(label, texto: str):
    global registro
    registro += texto
    if len(registro) > 15:
        registro = registro[-15:]
    label.config(text=registro, bg="black", fg="white",
                 font=("Helvetica", 24, "bold"))
    label.place(relx=0.5, rely=0.9, anchor="center")
    func_guardar_en_frecuencias(texto)


def func_mostrar_ventana_confirmacion(palabra_detectada: str):
    respuesta = messagebox.askyesno(
        "Confirmación",
        f"¿La detección de '{palabra_detectada}' fue correcta?"
    )
    if respuesta:
        func_guardar_en_binario(1)
    else:
        func_guardar_en_binario(0)
        func_guardar_error(palabra_detectada)
        func_corregir_palabra(palabra_detectada)
    global registro
    registro = ""


def func_corregir_palabra(palabra_detectada: str):
    correccion = simpledialog.askstring(
        "Corrección", f"Ingrese la corrección para '{palabra_detectada}':")
    if correccion:
        func_guardar_correccion(palabra_detectada, correccion.strip())

# --------------------------------------------------
# Modelo y etiquetas
# --------------------------------------------------
def func_safe_resize(img_crop: np.ndarray, target_size: tuple) -> np.ndarray:
    if img_crop.size == 0 or img_crop.shape[0] < MIN_CROP_SIZE or img_crop.shape[1] < MIN_CROP_SIZE:
        return np.ones((IMG_SIZE, IMG_SIZE, 3), np.uint8) * 128
    try:
        return cv2.resize(img_crop, target_size)
    except cv2.error:
        return np.ones(target_size + (3,), np.uint8) * 128


def func_cargar_etiquetas(ruta: str) -> Dict[int, str]:
    etiquetas: Dict[int, str] = {}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for line in f:
                linea = line.strip()
                if (not linea or
                        linea.startswith("Class Index Mapping") or
                        linea.startswith("=")):
                    continue
                if ":" not in linea:
                    continue
                idx_txt, nombre = linea.split(":", 1)
                idx_txt = idx_txt.strip()
                nombre = nombre.strip()
                if not idx_txt.isdigit():
                    continue
                idx = int(idx_txt)
                etiquetas[idx] = nombre
    except Exception as e:
        logger.error(f"Error al cargar etiquetas: {e}")
    return etiquetas

# --------------------------------------------------
# Bucle principal de imagen
# --------------------------------------------------
def func_actualizar_imagen():
    global last_update_time, gesto_actual, tiempo_inicio_gesto
    global capturado, sugerencias
    global gesto_siguiente_inicio, gesto_seleccionar_inicio
    global frame_count, last_fps_time, current_fps

    success, img = cap.read()
    if success:
        # FPS
        frame_count += 1
        now = time.time()
        if now - last_fps_time >= 1.0:
            current_fps = frame_count / (now - last_fps_time)
            frame_count = 0
            last_fps_time = now
            if fps_label:
                fps_label.config(text=f"FPS: {current_fps:.1f}")

        imgOutput = img.copy()
        hands, _ = detector.findHands(img)

        texto_detectado = ""

        if hands:
            try:
                hand = hands[0]
                x, y, w, h = hand["bbox"]

                if w < MIN_CROP_SIZE or h < MIN_CROP_SIZE:
                    root.after(10, func_actualizar_imagen)
                    return

                x1, y1 = max(0, x - OFFSET), max(0, y - OFFSET)
                x2, y2 = min(img.shape[1], x + w + OFFSET), min(img.shape[0], y + h + OFFSET)
                imgCrop = img[y1:y2, x1:x2]

                if imgCrop.size == 0:
                    root.after(10, func_actualizar_imagen)
                    return

                imgWhite = np.ones((IMG_SIZE, IMG_SIZE, 3), np.uint8) * 255
                aspectRatio = h / w

                if aspectRatio > 1:
                    k = IMG_SIZE / h
                    wCal = math.ceil(k * w)
                    imgResize = func_safe_resize(imgCrop, (wCal, IMG_SIZE))
                    wGap = math.ceil((IMG_SIZE - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                else:
                    k = IMG_SIZE / w
                    hCal = math.ceil(k * h)
                    imgResize = func_safe_resize(imgCrop, (IMG_SIZE, hCal))
                    hGap = math.ceil((IMG_SIZE - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize

                imgWhite = cv2.resize(imgWhite, (224, 224))
                prediction, index = classifier.getPrediction(imgWhite, draw=False)

                if index in labels:
                    texto_detectado = labels[index]
                    # marker color changed to RED
                    cv2.putText(imgOutput, texto_detectado,
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_COMPLEX,
                                1, (0, 0, 255), 2)
                    cv2.rectangle(imgOutput, (x1, y1), (x2, y2),
                                  (0, 0, 255), 3)

                logger.debug(f"PRED {prediction} INDEX {index} LABEL {texto_detectado}")
                root.title(f"🤲 Gesto detectado: {texto_detectado}")

            except Exception as e:
                logger.error(f"Error procesando mano: {e}")

        current_time = time.time()

        # Gestos especiales
        if texto_detectado == "Siguiente":
            if gesto_siguiente_inicio is None:
                gesto_siguiente_inicio = current_time
            elif current_time - gesto_siguiente_inicio >= tiempo_espera_siguiente:
                func_resaltar_siguiente(sugerencias)
                gesto_siguiente_inicio = None
        else:
            gesto_siguiente_inicio = None

        if texto_detectado == "Seleccionar":
            if gesto_seleccionar_inicio is None:
                gesto_seleccionar_inicio = current_time
            elif current_time - gesto_seleccionar_inicio >= tiempo_espera_seleccionar:
                func_seleccionar_palabra(sugerencias)
                gesto_seleccionar_inicio = None
        else:
            gesto_seleccionar_inicio = None

        # Gestos normales (requiere ~1 segundo)
        if texto_detectado and texto_detectado not in ["Siguiente", "Seleccionar"]:
            if texto_detectado == gesto_actual and not capturado:
                if current_time - tiempo_inicio_gesto >= tiempo_espera_gestos:
                    logger.info(f"Añadiendo al subtítulo: {texto_detectado}")
                    func_actualizar_subtitulos(subtitulo_label, texto_detectado)
                    porcentaje_similitud = similarity_slider.get()
                    sugerencias = func_obtener_sugerencias(
                        registro, diccionario, porcentaje_similitud)
                    func_mostrar_sugerencias(sugerencias_label, sugerencias)
                    capturado = True
                    last_update_time = current_time
            else:
                gesto_actual = texto_detectado
                tiempo_inicio_gesto = current_time
                capturado = False

        if capturado and current_time - last_update_time >= tiempo_espera_post_captura:
            capturado = False

        # Actualizar imagen en tkinter
        imgRGB = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2RGB)
        imgPIL = Image.fromarray(imgRGB)
        width = root.winfo_width() - 20
        height = root.winfo_height() - 100
        if width <= 0 or height <= 0:
            root.after(10, func_actualizar_imagen)
            return
        imgPIL = imgPIL.resize((width, height))
        imgTK = ImageTk.PhotoImage(imgPIL)
        imagen_label.config(image=imgTK)
        imagen_label.image = imgTK

    root.after(10, func_actualizar_imagen)

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Modelo no encontrado: {MODEL_PATH}")
        exit(1)
    if not os.path.exists(LABELS_PATH):
        print(f"❌ Etiquetas no encontradas: {LABELS_PATH}")
        exit(1)

    root = tk.Tk()
    root.title("🤲 Reconocimiento de Lengua de Señas")
    root.geometry("1280x720")
    root.configure(bg="#8e8ca3")

    imagen_label = tk.Label(root)
    imagen_label.place(x=0, y=0, relwidth=1, relheight=0.7)

    similarity_slider = tk.Scale(root, from_=1, to=100, orient="horizontal",
                                 label="Similitud (%)", bg="#8e8ca3")
    similarity_slider.place(x=120, y=520)
    similarity_slider.set(60)

    # FPS label at left top of subtitles
    fps_label = tk.Label(root, text="FPS: 0.0", bg="black", fg="white",
                         font=("Helvetica", 10, "bold"))
    fps_label.place(x=20, y=670)

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = HandDetector(maxHands=1)
    classifier = Classifier(MODEL_PATH, LABELS_PATH)
    labels = func_cargar_etiquetas(LABELS_PATH)
    diccionario = func_cargar_diccionario(DICT_PATH)

    print("DEBUG labels:", labels)
    print("DEBUG diccionario size:", len(diccionario))

    subtitulo_label = tk.Label(root, text="", bg="black", fg="white",
                               font=("Helvetica", 24, "bold"))
    sugerencias_label = tk.Label(root, text="", bg="black", fg="white",
                                 font=("Helvetica", 18, "bold"))

    xBtn = 100
    func_crear_boton(root, "Configuración", func_conf, xBtn, 60)
    func_crear_boton(root, "Alfabeto", func_alph, xBtn, 120)
    func_crear_boton(root, "Captura", func_captures, xBtn, 180)
    func_crear_boton(root, "Reiniciar", func_reiniciar_deteccion, xBtn, 240)

    logger.info("✅ GUI Gesture Recognition Started")
    func_actualizar_imagen()
    root.mainloop()

    if cap:
        cap.release()
    cv2.destroyAllWindows()
