import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURACIÓN ---
archivo = r"C:\Users\neotr\OneDrive\Escritorio\ENTREGABLES_UNAL_HUMEDALES\Resultados_Calidad_Agua_HCordoba.xlsx"
salida_dir = r"C:\Users\neotr\OneDrive\Escritorio\ENTREGABLES_UNAL_HUMEDALES\SALIDAS"
os.makedirs(salida_dir, exist_ok=True)

# --- ESTILO GLOBAL ---
sns.set_style("whitegrid")
plt.rcParams.update({
    "axes.titlesize": 22,       # Tamaño del título
    "axes.labelsize": 18,       # Tamaño de etiquetas de ejes
    "xtick.labelsize": 16,      # Tamaño de etiquetas del eje X
    "ytick.labelsize": 16,      # Tamaño de etiquetas del eje Y
    "legend.fontsize": 16,      # Tamaño del texto de leyendas
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"]
})

# --- LECTURA DE DATOS ---
df = pd.read_excel(archivo)
df = df.set_index(df.columns[0])  # Primera columna = ID/Muestra

# --- Traducción de estadísticas ---
trad_stats = {
    'mean': 'Media',
    '50%': 'Mediana',
    'std': 'Desv. Estándar',
    'min': 'Mínimo',
    'max': 'Máximo'
}

# --- Diccionario de nombres y unidades ---
parametros = {
    "DQO": {"nombre": "DQO", "unidad": "mg/L O₂"},
    "pH": {"nombre": "pH", "unidad": "Unidades de pH"},
    "Fosfatos": {"nombre": "Fosfatos", "unidad": "mg/L"},
    "CE": {"nombre": "Conductividad Eléctrica", "unidad": "µS/cm"},
    "Turbidez": {"nombre": "Turbidez", "unidad": "NTU"},
    "Chl": {"nombre": "Clorofila-a", "unidad": "µg/L"},
    "ficocianina": {"nombre": "Ficocianina", "unidad": "µg/L"},
    "Nitratos ": {"nombre": "Nitratos", "unidad": "mg/L"},  # mantener si en Excel existe con espacio
    "Sulfatos": {"nombre": "Sulfatos", "unidad": "mg/L"}
}

# --- GENERAR ESTADÍSTICAS Y GRÁFICAS ---
for col in df.columns:
    # proteger datos no numéricos / NaN
    serie = pd.to_numeric(df[col], errors='coerce').dropna()

    if serie.empty:
        print(f"⚠️ Columna '{col}' no tiene valores numéricos. Se omitirá.")
        continue

    # Caso especial: pH -> calculamos métricas en antilog (concentración [H+]) y volvemos a log
    if col.strip().lower() == "ph" or col == "pH":
        # convertir pH -> [H+]
        H = 10 ** (-serie.values)  # array de concentraciones
        # estadísticas sobre [H+]
        mean_H = H.mean()
        median_H = np.median(H)
        std_H = H.std(ddof=1)  # desviación muestral
        min_H = H.min()
        max_H = H.max()

        # convertir estadísticas de [H+] de nuevo a pH
        mean_pH = -np.log10(mean_H)
        median_pH = -np.log10(median_H)
        # para min/max: recordar que pH es inverso: min_H -> max pH, max_H -> min pH
        min_pH = -np.log10(max_H)  # la menor concentración -> mayor pH
        max_pH = -np.log10(min_H)  # la mayor concentración -> menor pH

        # propagar desviación (aprox lineal): sigma_pH ≈ (1/ln10) * (sigma_H / mean_H)
        sigma_pH = (1.0 / np.log(10)) * (std_H / mean_H)  # ≈ 0.434 * std_H/mean_H

        # Preparar stats en formato consistente para mostrar (usamos las etiquetas en español)
        stats_display = {
            'Media': mean_pH,
            'Mediana': median_pH,
            'Desv. Estándar': sigma_pH,
            'Mínimo': min_pH,
            'Máximo': max_pH
        }

        # Para guardar en texto, redondeamos y añadimos unidad de pH (sin unidad química)
        unidad = parametros.get(col, {}).get("unidad", "Unidades de pH")
        textstr = "\n".join([f"{k}: {v:.2f} {'' if 'Desv' in k else unidad if k!='Desv. Estándar' else ''}"
                             for k, v in stats_display.items()])

        # Dibujar boxplot con los valores originales de pH (para visualización)
        plt.figure(figsize=(9,7))
        sns.boxplot(y=serie, color="skyblue", width=0.4)
        sns.stripplot(y=serie, color="black", alpha=0.6, jitter=True)

        nombre = parametros.get(col, {}).get("nombre", col)
        plt.title(nombre, fontsize=22, fontweight="bold", pad=20)
        plt.ylabel(unidad, fontsize=18, fontweight="bold")
        plt.xlabel("", fontsize=16, fontweight="bold")
        plt.xticks(fontsize=16, fontweight="bold")
        plt.yticks(fontsize=16, fontweight="bold")

        plt.gca().text(1.05, 0.5, textstr, transform=plt.gca().transAxes,
                       fontsize=14, fontweight="bold", verticalalignment='center',
                       bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="black", lw=1.5))

        plt.tight_layout()
        plt.savefig(os.path.join(salida_dir, f"{nombre}_boxplot.png"), dpi=400, bbox_inches="tight")
        plt.close()

    else:
        # cálculo normal para otros parámetros (estadísticas directas)
        stats = serie.describe()[['mean', '50%', 'std', 'min', 'max']]
        stats = stats.rename(index=trad_stats)

        nombre = parametros.get(col, {}).get("nombre", col)
        unidad = parametros.get(col, {}).get("unidad", "")

        # Crear figura
        plt.figure(figsize=(9,7))
        sns.boxplot(y=serie, color="skyblue", width=0.4)
        sns.stripplot(y=serie, color="black", alpha=0.6, jitter=True)

        # Título y etiquetas en negrita y más grandes
        plt.title(nombre, fontsize=22, fontweight="bold", pad=20)
        plt.ylabel(unidad if unidad else "", fontsize=18, fontweight="bold")
        plt.xlabel("", fontsize=16, fontweight="bold")
        plt.xticks(fontsize=16, fontweight="bold")
        plt.yticks(fontsize=16, fontweight="bold")

        # Recuadro con estadísticas descriptivas
        textstr = "\n".join([f"{trad_stats.get(k,k)}: {v:.2f} {unidad}" if k in trad_stats.values() or k in trad_stats.keys()
                             else f"{k}: {v:.2f} {unidad}" for k, v in stats.items()])
        # asegurar formato correcto de las etiquetas en español
        # stats ya fue renombrado arriba, así que usamos la clave directamente
        textstr = "\n".join([f"{k}: {v:.2f} {unidad}" for k, v in stats.items()])

        plt.gca().text(1.05, 0.5, textstr, transform=plt.gca().transAxes,
                       fontsize=14, fontweight="bold", verticalalignment='center',
                       bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="black", lw=1.5))

        plt.tight_layout()
        plt.savefig(os.path.join(salida_dir, f"{nombre}_boxplot.png"), dpi=400, bbox_inches="tight")
        plt.close()

print(f"✅ Gráficas tipo boxplot generadas en la carpeta: {salida_dir} con tratamiento especial para pH.")