import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import os
import shutil
import subprocess

# Configuración de variables
batch_size = 32
target_size = (224, 224)
epochs = 30
learning_rate = 1e-4
patience_early_stopping = 8
patience_lr_schedule = 4
lr_reduce_factor = 0.5
dr_origen = "Datos/train/"
dr_destino = "Datos/validation/"
modelo_path = 'Modelo/modelo_gestos_mejorado.h5'
labels_path = 'Modelo/labels.txt'
script_reinicio = 'z_prcs_reinicio_metricos.py'
script_recarga = 'z_prcs_recargar_diccionario.py'

#Se crea la carpeta donde se hara la validación de las imagenes.
#La validación lo que hace es cambiar diversos valores de las imagenes para su entrenamiento 
def crear_directorio_validacion(dr_origen, dr_destino):
    if not os.path.exists(dr_destino):
        shutil.copytree(dr_origen, dr_destino)
        print(f'Directorio creado y copiado de {dr_origen} a {dr_destino}')
    else:
        for foldername, subfolders, filenames in os.walk(dr_origen):
            rel_path = os.path.relpath(foldername, dr_origen)
            dest_folder = os.path.join(dr_destino, rel_path)

            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            for filename in filenames:
                src_file = os.path.join(foldername, filename)
                dest_file = os.path.join(dest_folder, filename)
                if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
                    shutil.copy2(src_file, dest_file)
                    print(f'Archivo copiado: {src_file} -> {dest_file}')

# Genera diferentes variables de las imágenes que le pasamos para un 
# mejor entrenamiento del modelo
# Haciendo estas variables para train y para validation
def generar_datos(batch_size=batch_size, target_size=target_size):
    train_datagen = ImageDataGenerator(
        rescale=1./255, 
        shear_range=0.2, 
        zoom_range=0.2, 
        horizontal_flip=True,
        rotation_range=20,  
        width_shift_range=0.2,
        height_shift_range=0.2,
        brightness_range=[0.8, 1.2],
    )

    test_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        'Datos/train/',
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical')

    validation_generator = test_datagen.flow_from_directory(
        'Datos/validation/',
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical')

    return train_generator, validation_generator

# Se construye el modelo basándonos en el modelo mobilenet, pasamos las categorías
# y diferentes parámetros 
def construir_modelo_transfer_learning(num_clases, input_shape=target_size + (3,)):
    base_model = tf.keras.applications.MobileNetV2(input_shape=input_shape,
                                                   include_top=False,     # Omitimos las capas finales del modelo para meter las nuestras
                                                   weights='imagenet')    # Pasamos los mismos pesos de imagenet
    base_model.trainable = False  #Congelamos las capas del modelo base

    model = models.Sequential([
        base_model,                       # Le pasamos el modelo base, con el entrenamiento congelado y "sin cabeza"
        layers.GlobalAveragePooling2D(),  # Capa para prepararlo para recibir la información y vectorizarlo
        layers.Dense(256, activation='relu'), # Capa densa, 256 neuronas con activación relu para evitar aprendizajes negativos repetitivos
        layers.Dropout(0.5),              # Dropout del 50% 
        layers.Dense(num_clases, activation='softmax') # capa densa de salida para una mejor clasificación de las categorías usando la activación softmax
    ])

    return model

def entrenar_modelo(model, train_generator, validation_generator, epochs=epochs):
    # Compilación del modelo
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), 
                  loss='categorical_crossentropy', metrics=['accuracy'])
    # early stopping nos ayuda a evitar un sobreentrenamiento innecesario, ya que detiene el entrenamiento si ve que no hay mejoras
    early_stopping = EarlyStopping(monitor='val_loss', patience=patience_early_stopping, restore_best_weights=True)
    # reducelr ayuda a que si detecta que no hay mejora en val_loss se pueda reducir la tasa de aprendizaje para un mejor funcionamiento
    lr_schedule = ReduceLROnPlateau(monitor='val_loss', factor=lr_reduce_factor, patience=patience_lr_schedule, verbose=1)

    # Pasamos el modelo que ya definimos con parámetros ya establecidos
    history = model.fit(
        train_generator, #Información con la que trabajará
        epochs=epochs,   # épocas
        validation_data=validation_generator,  # Datos de validación
        callbacks=[early_stopping, lr_schedule] # Métricas que tomará en cuenta que mencionamos antes
    )
    return history

def guardar_modelo_y_labels(model, train_generator, modelo_path=modelo_path, labels_path=labels_path):
    model.save(modelo_path)
    labels = train_generator.class_indices
    with open(labels_path, 'w') as f:
        for label, index in labels.items():
            f.write(f"{index} {label}\n")
    print(f'Modelo guardado en {modelo_path} y etiquetas en {labels_path}')

def ejecutar_scripts():
    try:
        subprocess.run(['python', script_reinicio], check=True)
        subprocess.run(['python', script_recarga], check=True)
        print("Scripts ejecutados exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script: {e}")

# Main
if __name__ == "__main__":
    # Paso 1: Copiar datos
    crear_directorio_validacion(dr_origen, dr_destino)

    # Paso 2: Generar datos
    train_generator, validation_generator = generar_datos()

    # Paso 3: Construir modelo con transfer learning
    model = construir_modelo_transfer_learning(train_generator.num_classes)

    # Paso 4: Entrenar modelo
    entrenar_modelo(model, train_generator, validation_generator)

    # Paso 5: Guardar modelo y etiquetas
    guardar_modelo_y_labels(model, train_generator)

    # Paso 6: Ejecutar scripts adicionales
    ejecutar_scripts()
