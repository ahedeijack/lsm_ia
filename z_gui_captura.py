"""
Hand Gesture Capture System (Console Edition)
=============================================
Real-time hand detection → crop → save for training.

Controls:
- 'c' = Capture image  
- 'n' = New folder name
- 'd' = Delete ALL data (type DELETE to confirm)
- 'q' = Quit

Author: Enhanced console version
Date: December 2025
"""

import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global configuration
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300
folder = ""
counter = 0
imgWhite = None
current_folder_label = "No folder selected"

def func_clear_screen():
    """Clear console screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def func_create_folder(folder_name: str):
    """Create gesture folder in Datos/train/."""
    global folder, counter, current_folder_label
    
    if folder_name.strip():
        folder = f"Datos/train/{folder_name.strip()}"
        os.makedirs(folder, exist_ok=True)
        
        # Count existing images
        counter = len([f for f in os.listdir(folder) if f.endswith('.jpg')])
        current_folder_label = f"{folder_name.strip()} ({counter} images)"
        
        logger.info(f"✅ Directorio creado: {folder}")
        print(f"📁 Folder ready: {folder}")
    else:
        print("❌ Por favor ingresa un nombre válido.")

def func_take_capture():
    """Save cropped hand image."""
    global counter, imgWhite
    
    if imgWhite is not None and folder:
        filename = f'{folder}/Image_{counter:04d}.jpg'
        cv2.imwrite(filename, imgWhite)
        print(f'📸 Imagen guardada: {filename}')
        counter += 1
        current_folder_label = f"{Path(folder).name} ({counter} images)"
    else:
        print("❌ No se puede guardar. Necesitas: 1) Mano detectada 2) Carpeta creada")

def func_delete_all():
    """Delete all training data (SAFE confirmation)."""
    print("\n⚠️  ELIMINAR TODO?")
    print("Esto borra Datos/train/ y Datos/validation/")
    confirm = input("Escribe 'DELETE' para confirmar: ").strip().upper()
    
    if confirm == "DELETE":
        train_folder = "Datos/train"
        validation_folder = "Datos/validation"
        
        if os.path.exists(train_folder):
            shutil.rmtree(train_folder)
            os.makedirs(train_folder)
            print("✅ train/ eliminado")
        
        if os.path.exists(validation_folder):
            shutil.rmtree(validation_folder)
            os.makedirs(validation_folder)
            print("✅ validation/ eliminado")
        
        global folder, counter, current_folder_label
        folder = ""
        counter = 0
        current_folder_label = "ALL DATA DELETED"
    else:
        print("❌ Cancelado")

def func_show_status():
    """Show live status."""
    func_clear_screen()
    print("=" * 60)
    print("🤲 CAPTURA DE GESTOS MANUAL")
    print("=" * 60)
    print(f"📁 {current_folder_label}")
    print(f"🖐️  Mano detectada: {'✅' if imgWhite is not None else '❌'}")
    print("\nCONTROLES:")
    print("  'c' = 📸 Tomar captura")
    print("  'n' = 📁 Nuevo directorio")
    print("  'd' = 🗑️  Eliminar TODO")
    print("  'q' = 🚪 Salir")
    print("=" * 60)

def func_hand_capture():
    """Main capture loop."""
    global imgWhite
    
    print("🎥 Cámara iniciada. Coloca tu mano frente a la cámara.")
    
    while True:
        success, img = cap.read()
        if not success:
            logger.error("No camera")
            break
            
        hands, img = detector.findHands(img)
        
        # Status text
        status = f"Folder: {current_folder_label} | Capturas: {counter}"
        cv2.putText(img, status, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if hands:
            try:
                hand = hands[0]
                x, y, w, h = hand['bbox']
                
                # White background
                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                
                # Crop hand
                imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
                
                # Resize maintaining aspect ratio
                aspectRatio = h / w
                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    wGap = math.ceil((imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                else:
                    k = imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    hGap = math.ceil((imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize
                
                # Show cropped hand
                cv2.imshow("Mano Recortada (Listo para guardar)", imgWhite)
                
            except Exception as e:
                logger.error(f"Error processing hand: {e}")
        
        cv2.imshow("Cámara - 'c' para capturar", img)
        func_show_status()
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            func_take_capture()
        elif key == ord('n'):
            folder_name = input("Nombre del gesto (ej: palm_up): ").strip()
            func_create_folder(folder_name)
        elif key == ord('d'):
            func_delete_all()

# Main execution
if __name__ == "__main__":
    try:
        # Create base directories
        os.makedirs("Datos/train", exist_ok=True)
        os.makedirs("Datos/validation", exist_ok=True)
        
        func_hand_capture()
        
    except KeyboardInterrupt:
        print("\n👋 Interrumpido por usuario")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Sesión terminada")
