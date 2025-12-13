"""
z_prcs_packages.py
------------------
Utility script to prepare the environment for the LSM project:

- Creates required folders
- Creates placeholder analysis files if they do not exist
- Installs required Python packages via pip
"""

import os
import sys
import subprocess
from pathlib import Path

# --------------------------------------------------
# Project paths (relative to this file)
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DIRS_TO_CREATE = [
    BASE_DIR / "Modelo",
    BASE_DIR / "Datos",
    BASE_DIR / "Datos" / "Analisis",
    BASE_DIR / "Datos" / "Capturas",
]

FILES_TO_TOUCH = [
    BASE_DIR / "Datos" / "Analisis" / "z_frecuencias.txt",
    BASE_DIR / "Datos" / "Analisis" / "z_binarios.txt",
    BASE_DIR / "Datos" / "Analisis" / "z_errores.txt",
    BASE_DIR / "Datos" / "Analisis" / "z_correciones.txt",
    BASE_DIR / "Datos" / "Analisis" / "z_info_diccionario.txt",
]

# If you already have the model + labels, you do NOT recreate them here.
MODEL_FILE = BASE_DIR / "Modelo" / "mejor_modelo_gestos.h5"
LABELS_FILE = BASE_DIR / "Modelo" / "labels.txt"

# --------------------------------------------------
# Packages to install
# --------------------------------------------------
REQUIRED_PACKAGES = [
    "opencv-python",
    "opencv-contrib-python",
    "cvzone",
    "tensorflow",      # or 'tensorflow-macos' on Apple Silicon if you prefer
    "numpy",
    "pillow",
]

def run_command(cmd):
    """Run a shell command and stream its output."""
    print(f"\n[CMD] {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Command failed with code {result.returncode}: {' '.join(cmd)}")
    return result.returncode

def create_directories():
    print("\n==> Creating directories (if missing)...")
    for d in DIRS_TO_CREATE:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  - {d}")

def touch_files():
    print("\n==> Creating placeholder analysis files (if missing)...")
    for f in FILES_TO_TOUCH:
        if not f.exists():
            f.touch()
            print(f"  - Created {f}")
        else:
            print(f"  - Exists {f}")

def show_model_warning():
    print("\n==> Model and label files")
    if not MODEL_FILE.exists():
        print(f"  ! Missing model file: {MODEL_FILE}")
        print("    Place your trained 'mejor_modelo_gestos.h5' in the 'Modelo' folder.")
    else:
        print(f"  - Found model file: {MODEL_FILE}")

    if not LABELS_FILE.exists():
        print(f"  ! Missing labels file: {LABELS_FILE}")
        print("    Place your 'labels.txt' (with index: label format) in the 'Modelo' folder.")
    else:
        print(f"  - Found labels file: {LABELS_FILE}")

def install_packages():
    print("\n==> Installing required Python packages with pip...")
    # Use the same Python executable that runs this script
    python_exe = sys.executable

    # On Apple Silicon, user might want tensorflow-macos instead of tensorflow
    packages = REQUIRED_PACKAGES.copy()
    if sys.platform == "darwin" and "arm" in subprocess.check_output(["uname", "-m"]).decode().strip():
        # Optionally suggest tensorflow-macos
        print("Detected macOS on Apple Silicon. You may prefer 'tensorflow-macos'.")
        print("If 'tensorflow' fails, install 'tensorflow-macos' manually.")
    cmd = [python_exe, "-m", "pip", "install"] + packages
    run_command(cmd)

def main():
    print("===============================================")
    print("  LSM Project Setup - z_prcs_packages.py")
    print("===============================================\n")

    print(f"Using Python: {sys.executable}")
    print(f"Project root: {BASE_DIR}\n")

    create_directories()
    touch_files()
    show_model_warning()
    install_packages()

    print("\n✅ Setup complete (or attempted).")
    print("   Next steps:")
    print("   - Ensure your model (.h5) and labels.txt are in the 'Modelo' folder.")
    print("   - Then run your main GUI, e.g.:")
    print("       python zguiinterfaz.py")
    print("")

if __name__ == "__main__":
    main()
