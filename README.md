# WQ_ML – Modelado de Calidad de Agua con Aprendizaje computacional

## Descripción general
Este repositorio contiene un flujo completo de análisis, modelado y espacialización de parámetros de calidad de agua a partir de información espectral y variables auxiliares, utilizando técnicas de Machine Learning. El código principal se encuentra en el notebook `WQ_ML.ipynb`.

El objetivo es predecir parámetros fisicoquímicos de calidad de agua a partir de datos extraídos previamente de imágenes satelitales (por ejemplo, Landsat) y almacenados en un Shapefile, para posteriormente reconstruir los resultados en formato espacial (raster).

---

## Objetivos del proyecto
- Explorar estadísticamente variables predictoras y variables respuesta de calidad de agua.
- Evaluar el efecto de transformaciones logarítmicas en las variables respuesta.
- Entrenar y comparar diferentes modelos de Machine Learning.
- Validar el desempeño de los modelos mediante métricas estadísticas.
- Reconstruir espacialmente las predicciones generadas por los modelos.

---

## Librerías utilizadas
El proyecto hace uso de librerías especializadas en:

### Análisis y visualización
- matplotlib
- seaborn
- plotly

### Manejo de datos espaciales
- geopandas
- shapely
- rasterio

### Machine Learning
- scikit-learn
  - Support Vector Regression (SVR)
  - Random Forest Regressor (RFR)
  - Gradient Boosting Regressor (GBR)

### Procesamiento numérico
- numpy
- pandas

---

## Estructura del flujo de trabajo

### 1. Carga de librerías
Se inicializan todas las librerías necesarias para análisis estadístico, visualización, modelado y procesamiento espacial.

---

### 2. Carga del conjunto de datos
- El archivo de entrada es un Shapefile.
- Este Shapefile debe ser el mismo generado previamente mediante el script:

  Extract_Raster_Values.py

- Contiene:
  - Variables predictoras (bandas espectrales, índices, etc.).
  - Variables respuesta (parámetros de calidad de agua medidos in situ).

---

### 2.1 Transformación logarítmica
Se evalúan dos escenarios:

1. Variables respuesta transformadas a escala logarítmica.
2. Variables respuesta sin transformar.

Esta decisión se fundamenta en literatura previa, donde se reportan mejores desempeños al aplicar transformaciones logarítmicas sobre parámetros de calidad de agua.

---

### 2.2 Estadísticas descriptivas
Se realiza un análisis exploratorio que incluye:
- Estadísticos básicos (media, desviación estándar, valores mínimos y máximos).
- Revisión de distribuciones de las variables.

---

### 2.3 Análisis de correlación
Se calculan matrices de correlación de Pearson para:
- Variables respuesta transformadas.
- Variables respuesta sin transformar.

Las matrices se visualizan mediante mapas de calor, lo que permite:
- Identificar multicolinealidad.
- Evaluar relaciones entre predictores y variables respuesta.

---

## Modelado con Machine Learning

### Modelos implementados
Se entrenan y comparan los siguientes modelos de regresión:
- Support Vector Regression (SVR)
- Random Forest Regressor (RFR)
- Gradient Boosting Regressor (GBR)

Cada modelo se ajusta bajo ambos escenarios:
- Variables respuesta transformadas.
- Variables respuesta sin transformar.

---

### Preparación de los datos
- Selección de variables predictoras.
- Separación en conjuntos de entrenamiento y validación.
- Normalización o escalamiento cuando es requerido por el modelo.

---

### Evaluación de modelos
El desempeño de los modelos se evalúa mediante métricas como:
- Coeficiente de determinación (R²).
- Error cuadrático medio (RMSE).
- Error absoluto medio (MAE).

Los resultados permiten comparar modelos entre sí y analizar el impacto de la transformación logarítmica.

---

## Reconstrucción espacial de resultados

Una vez entrenados los modelos:
- Las predicciones se generan en forma de vectores.
- Estos vectores se reconstruyen a su forma espacial original (H × W).
- Si las predicciones se realizaron en escala logarítmica, se aplica la transformación inversa para recuperar los valores reales.

El resultado final puede exportarse como raster o visualizarse mediante mapas temáticos.

---

## Visualización de resultados
El notebook incluye:
- Gráficos de dispersión entre valores observados y predichos.
- Mapas temáticos de los parámetros de calidad de agua.
- Comparación visual entre modelos.

---

## Requisitos

Python 3.9 o superior

Instalación de dependencias sugerida:

pip install numpy pandas geopandas rasterio scikit-learn matplotlib seaborn plotly

---

## Ejecución
1. Generar el Shapefile de entrada usando `Extract_Raster_Values.py`.
2. Abrir el notebook `WQ_ML.ipynb`.
3. Ejecutar las celdas en orden secuencial.

---

## Notas importantes
- La calidad del modelo depende fuertemente de la representatividad de los datos de campo.
- Se recomienda evaluar cuidadosamente la transformación logarítmica según el parámetro de calidad de agua.
- El flujo puede adaptarse fácilmente a otros sensores o regiones.

---

## Autor
Universidad Nacional de Colombia 

---

## Licencia
Este proyecto se distribuye bajo licencia libre para fines académicos y de investigación. Puedes adaptarlo y reutilizarlo citando la fuente.
