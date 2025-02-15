import unicodedata
import tkinter as tk
from tkinter import messagebox

#Convertimos el texto a mayusculas y eliminamos caracteres especiales para tener un mejor rendimineto 
def func_limpiar_texto(texto):
    #-Convertimos el texto a mayusculas, posteriormente eliminamos caracteres especiales y finalmente, quitamos todo lo 
    #que no sea una letra o espacio
    texto = texto.upper()
    
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    
    texto = ''.join(c for c in texto if c.isalnum() or c.isspace())
    
    return texto

#Mostramos a nuestro usuario según el fragmento donde se llamo
def func_mostrar_alerta(mensaje):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Proceso Completado", mensaje)
    root.destroy()

#Aquí integramos la funcion de limpiar. pidiendo un directorio de un archivo de entra y uno de salida 
def func_procesar_archivo(archivo_entrada, archivo_salida):
    with open(archivo_entrada, 'r', encoding='utf-8') as file:
        contenido = file.read()
    
    contenido_limpio = func_limpiar_texto(contenido)
    palabras = contenido_limpio.split()
    func_mostrar_alerta(f"Archivo procesado. Número de palabras: {len(palabras)}")
    
    with open(archivo_salida, 'w', encoding='utf-8') as file:
        for palabra in palabras:
            file.write(palabra + '\n')

#En caso de ser necesario, eliminamos registros duplicados que puedan afectar el rendimiento de nuestro modeloo
def func_eliminar_duplicados(archivo):
    with open(archivo, 'r', encoding='utf-8') as file:
        contenido = file.readlines()
    
    palabras_unicas = list(set(contenido))
    func_mostrar_alerta(f"Duplicados eliminados. Número de palabras únicas: {len(palabras_unicas)}")
    
    with open(archivo, 'w', encoding='utf-8') as file:
        file.writelines(palabras_unicas)

#Ubicacion de nuestros archivos de entrad ay salida 
archivo_entrada = 'Datos/z_diccionaro_provicional.txt'
archivo_salida = 'Datos/Analisis/z_info_diccionario.txt'

#Processamos nuestros archivos y eliminamos nuestros duplicados
func_procesar_archivo(archivo_entrada, archivo_salida)
func_eliminar_duplicados(archivo_salida)
