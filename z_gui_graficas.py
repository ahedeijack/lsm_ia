import matplotlib.pyplot as plt
from collections import Counter
import difflib
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess
import os

# ------------- Lectura de datos -----------------
def func_leer_archivo_binarios(archivo="Datos/Analisis/z_binarios.txt"):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.read().splitlines()
    except FileNotFoundError:
        return []
    valores = []
    for linea in lineas:
        linea = linea.strip()
        if linea in ("0", "1"):
            valores.append(int(linea))
    return valores  # lista para poder hacer series


def func_leer_archivo_frecuencias(archivo="Datos/Analisis/z_frecuencias.txt"):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.read().splitlines()
    except FileNotFoundError:
        return Counter()
    etiquetas = [linea.strip() for linea in lineas if linea.strip()]
    return Counter(etiquetas)


def func_leer_archivo_correcciones(archivo="Datos/Analisis/z_correciones.txt"):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.read().splitlines()
    except FileNotFoundError:
        return []

    pares_palabras = []
    for linea in lineas:
        if " : " in linea:
            incorrecta, corregida = linea.split(" : ", 1)
            incorrecta = incorrecta.strip("' ").strip()
            corregida = corregida.strip("' ").strip()
            pares_palabras.append((incorrecta, corregida))
    return pares_palabras

# ------------- Gráficas básicas -----------------
def func_graficar_pastel(frecuencias_counter):
    # frecuencias_counter es Counter({0: ..., 1: ...})
    fig, ax = plt.subplots(figsize=(5, 4))
    fallos = frecuencias_counter.get(0, 0)
    aciertos = frecuencias_counter.get(1, 0)
    total = fallos + aciertos
    if total == 0:
        ax.text(0.5, 0.5, "No hay datos de aciertos/fallos", ha="center")
        ax.axis("off")
        return fig

    labels = ["Fallos (0)", "Aciertos (1)"]
    sizes = [fallos, aciertos]
    colors = ["#ff6b6b", "#51cf66"]
    explode = (0.05, 0.05)

    ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct="%1.1f%%",
        startangle=90,
        shadow=True,
    )
    ax.axis("equal")
    ax.set_title("Porcentaje de aciertos vs fallos", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig


def func_graficar_frecuencias(frecuencias):
    fig, ax = plt.subplots(figsize=(6, 4))
    if not frecuencias:
        ax.text(0.5, 0.5, "No hay datos de etiquetas", ha="center")
        ax.axis("off")
        return fig

    etiquetas = list(frecuencias.keys())
    conteo = list(frecuencias.values())

    bars = ax.bar(etiquetas, conteo, color="#4dabf7")
    ax.set_xlabel("Etiquetas")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Frecuencia de letras detectadas", fontsize=12, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                f"{int(height)}", ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    return fig

# ------------- Gráficas avanzadas -----------------
def func_graficar_evolucion_accuracy(lista_binarios):
    fig, ax = plt.subplots(figsize=(6, 4))
    if not lista_binarios:
        ax.text(0.5, 0.5, "No hay datos para la evolución", ha="center")
        ax.axis("off")
        return fig

    cumul_aciertos = []
    cumul_total = []
    aciertos = 0
    for i, val in enumerate(lista_binarios, start=1):
        if val == 1:
            aciertos += 1
        cumul_aciertos.append(aciertos)
        cumul_total.append(i)

    accuracy = [a / t * 100 for a, t in zip(cumul_aciertos, cumul_total)]

    ax.plot(cumul_total, accuracy, marker="o", color="#845ef7")
    ax.set_xlabel("Muestra (orden en el tiempo)")
    ax.set_ylabel("Accuracy acumulada (%)")
    ax.set_title("Evolución de la accuracy a lo largo del tiempo", fontsize=12, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.tight_layout()
    return fig


def func_comparar_palabras_con_porcentaje(original, corregida):
    d = difflib.ndiff(original, corregida)
    diferencias = list(d)
    errores = sum(1 for diff in diferencias if diff.startswith('-') or diff.startswith('+'))
    if max(len(original), len(corregida)) == 0:
        porcentaje_error = 0.0
    else:
        porcentaje_error = (errores / max(len(original), len(corregida))) * 100
    return diferencias, porcentaje_error


def func_graficar_comparacion_palabras(pares_palabras):
    if not pares_palabras:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "No hay correcciones para mostrar", fontsize=10, ha='center')
        ax.axis('off')
        return fig

    filas = min(len(pares_palabras), 4)
    fig, axes = plt.subplots(filas, 1, figsize=(8, 2.5 * filas), squeeze=False)

    for i in range(filas):
        original, corregida = pares_palabras[i]
        diferencias, porcentaje_error = func_comparar_palabras_con_porcentaje(original, corregida)
        letras = []
        colores = []

        for diff in diferencias:
            if diff.startswith(' '):
                letras.append(diff[2])
                colores.append('green')      # correcto
            elif diff.startswith('-'):
                letras.append(diff[2])
                colores.append('red')        # eliminado
            elif diff.startswith('+'):
                letras.append(diff[2])
                colores.append('orange')     # agregado

        ax = axes[i][0]
        ax.bar(range(len(letras)), [1] * len(letras), color=colores, tick_label=letras)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_title(f"'{original}' → '{corregida}'  (Error: {porcentaje_error:.1f}%)", fontsize=10)

    fig.suptitle("Comparación de palabras corregidas (verde=OK, rojo=-, naranja=+)", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def func_graficar_histograma_longitudes(pares_palabras):
    fig, ax = plt.subplots(figsize=(5, 3))
    if not pares_palabras:
        ax.text(0.5, 0.5, "No hay correcciones para mostrar", fontsize=10, ha='center')
        ax.axis('off')
        return fig

    longitudes_original = [len(o) for o, _ in pares_palabras]
    longitudes_corregida = [len(c) for _, c in pares_palabras]

    bins = range(0, max(longitudes_original + longitudes_corregida) + 2)

    ax.hist(longitudes_original, bins=bins, alpha=0.6, label="Original", color="#228be6")
    ax.hist(longitudes_corregida, bins=bins, alpha=0.6, label="Corregida", color="#fa5252")
    ax.set_xlabel("Longitud de palabra (caracteres)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Histograma de longitudes de palabras", fontsize=11, fontweight="bold")
    ax.legend()
    fig.tight_layout()
    return fig

# ------------- Helper para mostrar gráfica en Tk -------------
def func_embebed_figure(frame, fig):
    for child in frame.winfo_children():
        child.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return canvas

# ------------- Interfaz Tkinter -----------------
class InterfazGraficas:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de rendimiento del modelo")
        self.root.geometry("1000x650")

        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel superior: resumen + botones
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        self.label_resumen = ttk.Label(top_frame, text="", font=("Helvetica", 10))
        self.label_resumen.pack(side=tk.LEFT)

        boton_refrescar = ttk.Button(top_frame, text="Refrescar datos", command=self.func_refrescar_datos)
        boton_refrescar.pack(side=tk.RIGHT, padx=5)

        boton_volver = ttk.Button(top_frame, text="Volver a configuración", command=self.func_volver_a_config)
        boton_volver.pack(side=tk.RIGHT, padx=5)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.tab_pastel = ttk.Frame(self.notebook)
        self.tab_frecuencias = ttk.Frame(self.notebook)
        self.tab_evolucion = ttk.Frame(self.notebook)
        self.tab_correcciones = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_pastel, text="Aciertos vs Fallos")
        self.notebook.add(self.tab_frecuencias, text="Frecuencia de letras")
        self.notebook.add(self.tab_evolucion, text="Evolución en el tiempo")
        self.notebook.add(self.tab_correcciones, text="Correcciones")

        # Each tab: top bar with help button + figure frame
        self.frame_pastel_top = ttk.Frame(self.tab_pastel)
        self.frame_pastel_top.pack(fill=tk.X)
        ttk.Button(self.frame_pastel_top, text="?",
                   width=3,
                   command=self.func_help_pastel).pack(side=tk.RIGHT, padx=5, pady=5)
        self.frame_pastel = ttk.Frame(self.tab_pastel)
        self.frame_pastel.pack(fill=tk.BOTH, expand=True)

        self.frame_frec_top = ttk.Frame(self.tab_frecuencias)
        self.frame_frec_top.pack(fill=tk.X)
        ttk.Button(self.frame_frec_top, text="?",
                   width=3,
                   command=self.func_help_frecuencias).pack(side=tk.RIGHT, padx=5, pady=5)
        self.frame_frecuencias = ttk.Frame(self.tab_frecuencias)
        self.frame_frecuencias.pack(fill=tk.BOTH, expand=True)

        self.frame_evo_top = ttk.Frame(self.tab_evolucion)
        self.frame_evo_top.pack(fill=tk.X)
        ttk.Button(self.frame_evo_top, text="?",
                   width=3,
                   command=self.func_help_evolucion).pack(side=tk.RIGHT, padx=5, pady=5)
        self.frame_evolucion = ttk.Frame(self.tab_evolucion)
        self.frame_evolucion.pack(fill=tk.BOTH, expand=True)

        self.frame_corr_top = ttk.Frame(self.tab_correcciones)
        self.frame_corr_top.pack(fill=tk.X)
        ttk.Button(self.frame_corr_top, text="?",
                   width=3,
                   command=self.func_help_correcciones).pack(side=tk.RIGHT, padx=5, pady=5)
        self.frame_correcciones = ttk.Frame(self.tab_correcciones)
        self.frame_correcciones.pack(fill=tk.BOTH, expand=True)

        # estado
        self.canvas_pastel = None
        self.canvas_frecuencias = None
        self.canvas_evolucion = None
        self.canvas_correcciones = None

        self.func_refrescar_datos()

    def func_refrescar_datos(self):
        # Leer datos
        self.lista_binarios = func_leer_archivo_binarios()
        self.frecuencias_binarios = Counter(self.lista_binarios)
        self.frecuencias_etiquetas = func_leer_archivo_frecuencias()
        self.pares_palabras = func_leer_archivo_correcciones()

        # Resumen
        total = len(self.lista_binarios)
        fallos = self.frecuencias_binarios.get(0, 0)
        aciertos = self.frecuencias_binarios.get(1, 0)
        if total > 0:
            accuracy = (aciertos / total) * 100
            resumen = f"Total muestras: {total} | Aciertos: {aciertos} | Fallos: {fallos} | Accuracy: {accuracy:.1f}%"
        else:
            resumen = "No hay datos de aciertos/fallos todavía."
        if self.frecuencias_etiquetas:
            mas_comun, cnt = self.frecuencias_etiquetas.most_common(1)[0]
            resumen += f"  | Letra más frecuente: '{mas_comun}' ({cnt} veces)"
        self.label_resumen.config(text=resumen)

        # Figuras
        fig_pastel = func_graficar_pastel(self.frecuencias_binarios)
        fig_frec = func_graficar_frecuencias(self.frecuencias_etiquetas)
        fig_evo = func_graficar_evolucion_accuracy(self.lista_binarios)

        # Correcciones: combinamos barras de comparación + histograma de longitudes en una figura grande
                # Correcciones: listado + histograma de longitudes en una figura grande
        fig_corr = plt.figure(figsize=(9, 5))
        gs = fig_corr.add_gridspec(1, 2, width_ratios=[2, 1])

        # Subfigura 1: listado de algunas correcciones con porcentaje
        sub_fig1 = fig_corr.add_subplot(gs[0, 0])
        sub_fig1.axis('off')
        pares = self.pares_palabras[:5]  # hasta 5 para que quepa bien
        y0 = 0.85
        if pares:
            sub_fig1.set_title("Listado de correcciones recientes", fontsize=11, fontweight="bold")
            for (orig, corr) in pares:
                _, err = func_comparar_palabras_con_porcentaje(orig, corr)
                sub_fig1.text(
                    0.01,
                    y0,
                    f"'{orig}' → '{corr}'  (Error: {err:.1f}%)",
                    fontsize=9,
                    va="top"
                )
                y0 -= 0.15
        else:
            sub_fig1.text(0.5, 0.5, "No hay correcciones registradas", ha="center")
            sub_fig1.set_title("Listado de correcciones recientes", fontsize=11, fontweight="bold")

        # Subfigura 2: histograma de longitudes directamente en este eje
        sub_fig2 = fig_corr.add_subplot(gs[0, 1])
        if self.pares_palabras:
            longitudes_original = [len(o) for o, _ in self.pares_palabras]
            longitudes_corregida = [len(c) for _, c in self.pares_palabras]
            bins = range(0, max(longitudes_original + longitudes_corregida) + 2)

            sub_fig2.hist(
                longitudes_original,
                bins=bins,
                alpha=0.6,
                label="Original",
                color="#228be6"
            )
            sub_fig2.hist(
                longitudes_corregida,
                bins=bins,
                alpha=0.6,
                label="Corregida",
                color="#fa5252"
            )
            sub_fig2.set_xlabel("Longitud de palabra (caracteres)")
            sub_fig2.set_ylabel("Frecuencia")
            sub_fig2.set_title("Histograma de longitudes de palabras", fontsize=11, fontweight="bold")

            handles, labels = sub_fig2.get_legend_handles_labels()
            if handles:  # solo crear la leyenda si hay artistas con label
                sub_fig2.legend(handles=handles, labels=labels)
        else:
            sub_fig2.text(0.5, 0.5, "No hay correcciones para mostrar", fontsize=10, ha='center')
            sub_fig2.axis('off')

        fig_corr.tight_layout()

        # Embebemos
        self.canvas_pastel = func_embebed_figure(self.frame_pastel, fig_pastel)
        self.canvas_frecuencias = func_embebed_figure(self.frame_frecuencias, fig_frec)
        self.canvas_evolucion = func_embebed_figure(self.frame_evolucion, fig_evo)
        self.canvas_correcciones = func_embebed_figure(self.frame_correcciones, fig_corr)

    # ----- Ayuda de cada gráfica -----
    def func_help_pastel(self):
        messagebox.showinfo(
            "Aciertos vs Fallos",
            "Esta gráfica de pastel muestra la proporción de detecciones correctas (1) "
            "frente a detecciones incorrectas (0).\n\n"
            "Parámetros:\n"
            "- Fallos (0): número de veces que el usuario indicó que la palabra estaba mal.\n"
            "- Aciertos (1): número de veces que el usuario confirmó la detección como correcta.\n"
            "- Porcentaje: se calcula como (cantidad / total) * 100."
        )

    def func_help_frecuencias(self):
        messagebox.showinfo(
            "Frecuencia de letras",
            "La gráfica de barras muestra cuántas veces se ha detectado cada letra/etiqueta.\n\n"
            "Parámetros:\n"
            "- Eje X: letras/gestos detectados (por ejemplo A, E, I, O, U).\n"
            "- Eje Y: número de apariciones de cada letra en el archivo de frecuencias.\n"
            "- Etiquetas numéricas sobre cada barra indican el conteo exacto."
        )

    def func_help_evolucion(self):
        messagebox.showinfo(
            "Evolución en el tiempo",
            "La gráfica de línea muestra cómo evoluciona la accuracy acumulada "
            "a medida que se registran nuevas muestras.\n\n"
            "Parámetros:\n"
            "- Muestra: cada vez que se registra un resultado (correcto o incorrecto).\n"
            "- Accuracy acumulada: (aciertos acumulados / muestras totales) * 100.\n"
            "- Permite ver si el sistema mejora o empeora con el uso."
        )

    def func_help_correcciones(self):
        messagebox.showinfo(
            "Correcciones",
            "Este panel resume las palabras corregidas por el usuario.\n\n"
            "Parte izquierda:\n"
            "- Muestra algunas parejas 'palabra original' → 'palabra corregida'.\n"
            "- El porcentaje de error se basa en las diferencias de caracteres entre ambas.\n\n"
            "Parte derecha (histograma):\n"
            "- Compara la longitud (número de caracteres) de las palabras originales y corregidas.\n"
            "- Permite ver si las correcciones suelen hacer las palabras más largas o más cortas."
        )

    def func_volver_a_config(self):
        self.root.destroy()
        # Asegura que el archivo exista antes de llamar
        if os.path.exists("z_gui_conf.py"):
            subprocess.Popen(["python", "z_gui_conf.py"])
        else:
            messagebox.showwarning("Archivo no encontrado",
                                   "No se encontró 'z_gui_conf.py' en el directorio actual.")

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGraficas(root)
    root.mainloop()
