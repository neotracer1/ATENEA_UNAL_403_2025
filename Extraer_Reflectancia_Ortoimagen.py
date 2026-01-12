
import os
import numpy as np
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.windows import Window
from tqdm import tqdm

# Variables de entrada y de salida
raster_path = r"C:\Users\neotr\OneDrive\Escritorio\ENTREGABLES_UNAL_HUMEDALES\Imagenes\Humedal\Orto_Final\HC_10112025.tif"
points_path = r"C:\Users\neotr\OneDrive\Escritorio\ENTREGABLES_UNAL_HUMEDALES\Entregables_Humedal_Cordoba\SHP\Puntos_Muestreo_ON.shp"
excel_path  = r"C:\Users\neotr\OneDrive\Escritorio\ENTREGABLES_UNAL_HUMEDALES\Resultados_Calidad_Agua_HCordoba.xlsx"
output_path = r"C:\Users\neotr\OneDrive\Escritorio\ENTREGABLES_UNAL_HUMEDALES\Entregables_Humedal_Cordoba\SHP\Puntos_Muestreo_Reflectancia_Indices_Excel_2.shp"

# Tamaño de ventana (impar)
window_size = 11
offset = window_size // 2

# Nombres de las bandas de la camara Micasense RedEdge P
band_names = ["Blue", "Green", "Pan", "Red", "RedEdge", "NIR"]

# Definición de indices espectrales
candidate_predictors = [
    ("Blue",      lambda a: a[:,0]),
    ("Green",     lambda a: a[:,1]),
    ("Pan",       lambda a: a[:,2]),
    ("Red",       lambda a: a[:,3]),
    ("RedEdge",   lambda a: a[:,4]),
    ("NIR",       lambda a: a[:,5]),
    ("NDVI",      lambda a: (a[:,5]-a[:,3])/np.where((a[:,5]+a[:,3])==0,np.nan,a[:,5]+a[:,3])),
    ("NDWI",      lambda a: (a[:,1]-a[:,5])/np.where((a[:,1]+a[:,5])==0,np.nan,a[:,1]+a[:,5])),
    ("EVI",       lambda a: 2.5*(a[:,5]-a[:,3])/np.where((a[:,5]+6*a[:,3]-7.5*a[:,0]+1)==0,np.nan,a[:,5]+6*a[:,3]-7.5*a[:,0]+1)),
    ("SAVI",      lambda a: (1.5*(a[:,5]-a[:,3]))/np.where((a[:,5]+a[:,3]+0.5)==0,np.nan,a[:,5]+a[:,3]+0.5)),
    ("GNDVI",     lambda a: (a[:,5]-a[:,1])/np.where((a[:,5]+a[:,1])==0,np.nan,a[:,5]+a[:,1])),
    ("VARI",      lambda a: (a[:,1]-a[:,3])/np.where((a[:,1]+a[:,3]-a[:,0])==0,np.nan,a[:,1]+a[:,3]-a[:,0])),
    ("NDRE",      lambda a: (a[:,5]-a[:,4])/np.where((a[:,5]+a[:,4])==0,np.nan,a[:,5]+a[:,4])),
    ("CIgreen",   lambda a: (a[:,5]/np.where(a[:,1]==0,np.nan,a[:,1]))-1),
    ("CIRE",      lambda a: (a[:,5]/np.where(a[:,4]==0,np.nan,a[:,4]))-1),
    ("ARI",       lambda a: (1/np.where(a[:,1]==0,np.nan,a[:,1]))-(1/np.where(a[:,4]==0,np.nan,a[:,4]))),
    ("RENDVI",    lambda a: (a[:,5]-a[:,4])/np.where((a[:,5]+a[:,4])==0,np.nan,a[:,5]+a[:,4])),
]

# Cargar datos de entrada
print(" Cargando archivos...")
gdf = gpd.read_file(points_path)
df_excel = pd.read_excel(excel_path)

# Detectar columna de ID coincidente entre Excel y Shapefile
excel_id = df_excel.columns[0]
if excel_id in gdf.columns:
    merge_col = excel_id
elif "ID" in gdf.columns:
    merge_col = "ID"
elif "Name" in gdf.columns:
    merge_col = "Name"
else:
    raise ValueError("No se encontró una columna de ID coincidente entre shapefile y Excel.")

# Extraer reflectancias e índices
with rasterio.open(raster_path) as src:
    num_bandas = src.count
    if len(band_names) != num_bandas:
        band_names = [f"Banda_{i+1}" for i in range(num_bandas)]
        print("Se ajustaron nombres de banda automáticamente.")

    print(f" Raster con {num_bandas} bandas detectadas.")
    print(f" Calculando reflectancia promedio e índices (ventana {window_size}×{window_size})...")

    resultados = {label: [] for label, _ in candidate_predictors}

    for geom in tqdm(gdf.geometry, total=len(gdf)):
        if geom.is_empty or geom is None:
            for label in resultados.keys():
                resultados[label].append(np.nan)
            continue

        x, y = geom.x, geom.y
        row, col = src.index(x, y)
        window = Window(col - offset, row - offset, window_size, window_size)
        arr = np.array([src.read(b, window=window, boundless=True, fill_value=np.nan).flatten()
                        for b in range(1, num_bandas + 1)]).T

        for label, func in candidate_predictors:
            try:
                val = np.nanmean(func(arr))
            except Exception:
                val = np.nan
            resultados[label].append(val)

# Agregar resultados al GeoDataFrame
for label, values in resultados.items():
    gdf[label] = values

# Unir datos del Excel
print("\n Uniendo datos del Excel de laboratorio con los puntos...")
gdf = gdf.merge(df_excel, left_on=merge_col, right_on=excel_id, how="left")

# Guardar resultados
gdf.to_file(output_path)
print(f"\n Archivo generado con éxito:")
print(f"   {output_path}")
print("   Contiene reflectancias promedio, índices espectrales y parámetros de calidad de agua.")
