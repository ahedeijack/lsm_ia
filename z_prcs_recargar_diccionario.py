import unicodedata
import os

"""
Enhanced Dictionary Processing Script
=====================================
Processes text dictionary: cleans, removes duplicates, console output only
No tkinter dependency - works everywhere!
"""

def func_limpiar_texto(texto):
    """
    Clean text: uppercase, remove special chars, keep only letters/spaces.
    """
    texto = texto.upper()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = ''.join(c for c in texto if c.isalnum() or c.isspace())
    return texto

def func_mostrar_alerta(mensaje):
    """
    Console-based alert (replaces tkinter popup).
    """
    print(f"✅ {mensaje}")
    print("-" * 50)

def func_procesar_archivo(archivo_entrada, archivo_salida):
    """
    Process input file: clean text → word list → output file.
    """
    if not os.path.exists(archivo_entrada):
        print(f"❌ ERROR: Input file not found: {archivo_entrada}")
        return False
    
    with open(archivo_entrada, 'r', encoding='utf-8') as file:
        contenido = file.read()
    
    contenido_limpio = func_limpiar_texto(contenido)
    palabras = contenido_limpio.split()
    
    with open(archivo_salida, 'w', encoding='utf-8') as file:
        for palabra in palabras:
            file.write(palabra + '\n')
    
    func_mostrar_alerta(f"Archivo procesado. Número de palabras: {len(palabras)}")
    return True

def func_eliminar_duplicados(archivo):
    """
    Remove duplicate words from dictionary file.
    """
    if not os.path.exists(archivo):
        print(f"❌ ERROR: File not found: {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as file:
        contenido = file.readlines()
    
    palabras_unicas = list(set(contenido))
    palabras_unicas.sort()  # Alphabetical order
    
    with open(archivo, 'w', encoding='utf-8') as file:
        file.writelines(palabras_unicas)
    
    func_mostrar_alerta(f"Duplicados eliminados. Número de palabras únicas: {len(palabras_unicas)}")
    return True

# File paths
archivo_entrada = 'Datos/z_diccionaro_provicional.txt'
archivo_salida = 'Datos/Analisis/z_info_diccionario.txt'

print("🚀 Starting Dictionary Processing...")
print(f"📥 Input:  {archivo_entrada}")
print(f"📤 Output: {archivo_salida}")

# Ensure output directory exists
os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)

# Process pipeline
success = func_procesar_archivo(archivo_entrada, archivo_salida)
if success:
    func_eliminar_duplicados(archivo_salida)

print("✅ Dictionary processing completed!")
