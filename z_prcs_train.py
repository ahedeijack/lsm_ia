"""
Enhanced Gesture Recognition Model Training Script
================================================
This script trains a MobileNetV2-based transfer learning model for hand gesture classification.
Features:
- Automatic validation directory creation/sync
- Advanced data augmentation for training
- Transfer learning with frozen base model
- Early stopping and learning rate scheduling
- Model saving with class labels
- Post-training script execution

Author: Enhanced version
Date: December 2025
"""

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import os
import shutil
import subprocess
import logging
from typing import Tuple, Dict, Any
import matplotlib.pyplot as plt


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GestureTrainingConfig:
    """Configuration class for gesture recognition training parameters."""
    
    # Data processing
    BATCH_SIZE = 32
    TARGET_SIZE = (224, 224)
    EPOCHS = 50  # Increased for better convergence
    LEARNING_RATE = 1e-4
    
    # Callbacks
    PATIENCE_EARLY_STOPPING = 10
    PATIENCE_LR_SCHEDULE = 5
    LR_REDUCE_FACTOR = 0.5
    
    # Paths
    TRAIN_DIR = "Datos/train/"
    VALIDATION_DIR = "Datos/validation/"
    MODEL_PATH = 'Modelo/modelo_gestos_mejorado.h5'
    BEST_MODEL_PATH = 'Modelo/mejor_modelo_gestos.h5'
    LABELS_PATH = 'Modelo/labels.txt'
    HISTORY_PLOT_PATH = 'Modelo/training_history.png'
    
    # External scripts
    SCRIPT_REINICIO = 'z_prcs_reinicio_metricos.py'
    SCRIPT_RECARGA = 'z_prcs_recargar_diccionario.py'


def func_crear_directorio_validacion(dr_origen: str, dr_destino: str) -> None:
    """
    Create and synchronize validation directory from training data.
    
    This function ensures the validation directory exists and is synchronized
    with the training directory. It copies the directory structure and files,
    updating only newer files to avoid unnecessary copying.
    
    Args:
        dr_origen (str): Source training directory path
        dr_destino (str): Destination validation directory path
    
    Returns:
        None
    """
    if not os.path.exists(dr_destino):
        shutil.copytree(dr_origen, dr_destino, dirs_exist_ok=True)
        logger.info(f'Validation directory created and copied from {dr_origen} to {dr_destino}')
        return
    
    # Sync existing directory
    updated_files = 0
    for foldername, _, filenames in os.walk(dr_origen):
        rel_path = os.path.relpath(foldername, dr_origen)
        dest_folder = os.path.join(dr_destino, rel_path)
        
        os.makedirs(dest_folder, exist_ok=True)
        
        for filename in filenames:
            src_file = os.path.join(foldername, filename)
            dest_file = os.path.join(dest_folder, filename)
            
            if (not os.path.exists(dest_file) or 
                os.path.getmtime(src_file) > os.path.getmtime(dest_file)):
                shutil.copy2(src_file, dest_file)
                updated_files += 1
    
    logger.info(f'Validation directory synchronized. Updated {updated_files} files.')


def func_generar_datos_aumentados(batch_size: int, target_size: Tuple[int, int]) -> Tuple[Any, Any, Dict[str, int]]:
    """
    Generate training and validation data generators with augmentation.
    
    Enhanced data augmentation pipeline for robust gesture recognition:
    - Training: Rescaling, rotation, shear, zoom, flips, brightness, shifts
    - Validation: Only rescaling for clean evaluation
    
    Args:
        batch_size (int): Batch size for data generators
        target_size (Tuple[int, int]): Target image dimensions
        
    Returns:
        Tuple[Any, Any, Dict[str, int]]: (train_generator, validation_generator, class_indices)
    """
    # Enhanced training augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=25,      # Increased rotation
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=False,    # Disabled for gestures
        brightness_range=[0.7, 1.3],  # Wider brightness range
        fill_mode='nearest'
    )
    
    # Clean validation data
    validation_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        Config.TRAIN_DIR,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True
    )
    
    validation_generator = validation_datagen.flow_from_directory(
        Config.VALIDATION_DIR,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )
    
    logger.info(f'Data generators created. Found {train_generator.samples} training images, '
                f'{validation_generator.samples} validation images across {train_generator.num_classes} classes.')
    
    return train_generator, validation_generator, train_generator.class_indices


def func_construir_modelo_avanzado(num_clases: int, input_shape: Tuple[int, int, int]) -> models.Sequential:
    """
    Build enhanced MobileNetV2 transfer learning model.
    
    Architecture improvements:
    - Frozen MobileNetV2 base
    - Global Average Pooling
    - Multiple dense layers with batch normalization
    - Progressive dropout rates
    - Softmax output for multi-class classification
    
    Args:
        num_clases (int): Number of gesture classes
        input_shape (Tuple[int, int, int]): Input image shape (height, width, channels)
    
    Returns:
        models.Sequential: Compiled Keras model
    """
    # Load pre-trained MobileNetV2
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base model
    
    # Enhanced classification head
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(num_clases, activation='softmax', name='gestures_output')
    ])
    
    # Compile with improved optimizer
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=Config.LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'top_k_categorical_accuracy']
    )
    
    logger.info(f'Model built successfully: {model.summary()}')
    return model


def func_entrenar_modelo_robusto(model: models.Sequential, 
                                train_generator: Any, 
                                validation_generator: Any,
                                epochs: int) -> Dict[str, Any]:
    """
    Train model with comprehensive callbacks and monitoring.
    
    Args:
        model (models.Sequential): Compiled model
        train_generator (Any): Training data generator
        validation_generator (Any): Validation data generator
        epochs (int): Maximum training epochs
        
    Returns:
        Dict[str, Any]: Training history
    """
    # Enhanced callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=Config.PATIENCE_EARLY_STOPPING,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=Config.LR_REDUCE_FACTOR,
            patience=Config.PATIENCE_LR_SCHEDULE,
            min_lr=1e-7,
            verbose=1
        ),
        ModelCheckpoint(
            Config.BEST_MODEL_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Train model
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=validation_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # Plot training history
    func_plot_training_history(history)
    
    logger.info('Training completed successfully')
    return history.history


def func_plot_training_history(history) -> None:
    """Plot and save training history visualization."""
    # Use history.history to access metrics
    hist = history.history
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Accuracy plot
    ax1.plot(hist['accuracy'], label='Training Accuracy')
    ax1.plot(hist['val_accuracy'], label='Validation Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Loss plot
    ax2.plot(hist['loss'], label='Training Loss')
    ax2.plot(hist['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(Config.HISTORY_PLOT_PATH)
    plt.close()
    logger.info(f'Training history plot saved to {Config.HISTORY_PLOT_PATH}')


def func_guardar_modelo_completo(model: models.Sequential, 
                                class_indices: Dict[str, int], 
                                modelo_path: str, 
                                labels_path: str) -> None:
    """Save model and create human-readable labels file."""
    # Save complete model
    model.save(modelo_path)
    
    # Save class labels in human-readable format
    with open(labels_path, 'w') as f:
        f.write("Class Index Mapping (index: class_name):\n")
        f.write("=" * 40 + "\n")
        for label, index in sorted(class_indices.items()):
            f.write(f"{index:2d}: {label}\n")
    
    logger.info(f'Model saved to {modelo_path}')
    logger.info(f'Labels saved to {labels_path}')


def func_ejecutar_scripts_postentrenamiento() -> bool:
    """Execute post-training scripts safely."""
    scripts = [Config.SCRIPT_REINICIO, Config.SCRIPT_RECARGA]
    
    for script in scripts:
        if not os.path.exists(script):
            logger.warning(f'Script not found: {script}')
            continue
            
        try:
            result = subprocess.run(['python', script], 
                                  capture_output=True, text=True, check=True)
            logger.info(f'Script executed successfully: {script}')
        except subprocess.CalledProcessError as e:
            logger.error(f'Error executing {script}: {e.stderr}')
            return False
    
    return True


# Configuration instance
Config = GestureTrainingConfig()


def main() -> None:
    """Main training pipeline."""
    logger.info("Starting Enhanced Gesture Recognition Training Pipeline")
    
    # Ensure output directory exists
    os.makedirs('Modelo', exist_ok=True)
    
    # 1. Prepare validation data
    func_crear_directorio_validacion(Config.TRAIN_DIR, Config.VALIDATION_DIR)
    
    # 2. Create data generators
    train_gen, val_gen, class_indices = func_generar_datos_aumentados(
        Config.BATCH_SIZE, Config.TARGET_SIZE
    )
    
    # 3. Build model
    model = func_construir_modelo_avanzado(train_gen.num_classes, 
                                         Config.TARGET_SIZE + (3,))
    
    # 4. Train model
    history = func_entrenar_modelo_robusto(model, train_gen, val_gen, Config.EPOCHS)
    
    # 5. Save results
    func_guardar_modelo_completo(model, class_indices, 
                               Config.MODEL_PATH, Config.LABELS_PATH)
    
    # 6. Execute post-training scripts
    func_ejecutar_scripts_postentrenamiento()
    
    logger.info("Training pipeline completed successfully!")


if __name__ == "__main__":
    main()
