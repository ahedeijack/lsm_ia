import os

#Eliminamos el contenido dentro del archivo que se desea
def func_vaciar_archivo(nombre_archivo):
    ruta_archivo = os.path.join('Datos', 'Analisis', nombre_archivo)
    try:
        with open(ruta_archivo, 'w') as archivo:
            archivo.write('')
        print(f"El archivo '{ruta_archivo}' ha sido vaciado.")
    except FileNotFoundError:
        print(f"El archivo '{ruta_archivo}' no existe.")

#Metemos en un arreglo el nombre de nuestros archivos que deseamos limpiar y llamamos a la funcion para vaciarlos
def func_vaciar_todos_los_archivos():
    archivos = ['z_binarios.txt', 'z_errores.txt', 'z_frecuencias.txt', 'z_correciones.txt']
    for archivo in archivos:
        func_vaciar_archivo(archivo)

#Nuestro orquestador para eliminar los archivos
def func_ejecutar_vaciado():
    func_vaciar_todos_los_archivos()

#Nuestro inicio para ejecutrar el proceso
if __name__ == "__main__":
    func_ejecutar_vaciado()
