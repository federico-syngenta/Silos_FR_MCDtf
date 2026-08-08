# Documentación de Notebooks

Este documento resume el propósito y el flujo de trabajo de cada notebook en la carpeta `Nootebooks`. Incluye: propósito, requisitos, pasos principales, entradas/salidas, variables sensibles y notas de ejecución.

---

## 01_descarga_mensual_sentinel2_tiff.ipynb
Propósito:
- Buscar y descargar productos Sentinel-2 (L2A) desde Copernicus Data Space (ODATA) para un AOI y rango de fechas.
- Extraer los archivos .SAFE, combinar bandas a 10m y generar un composite RGB en GeoTIFF.

Requisitos:
- Paquetes: `sentinelhub`, `requests`, `rasterio`, `numpy`, `matplotlib`, `pandas`.
- Credenciales de Copernicus Data Space: `CDSE_CLIENT_ID`, `CDSE_CLIENT_SECRET` (recomendado: en `.env`).

Variables principales y configuración:
- `AOI`: lista [lon_min, lat_min, lon_max, lat_max].
- `START_DATE`, `END_DATE`: rango ISO (YYYY-MM-DD).
- `PLATFORM`: "S2A", "S2B", "S2C" o `None`.
- `DOWNLOAD_DIR`: carpeta donde se guardan los zips descargados (`sentinel2_complete_tiles`).
- `PROCESSED_DIR`: carpeta donde se guardan los composites RGB (`processed_tiles`).
- `MAX_PRODUCTS_TO_PROCESS`: limitar la cantidad de productos a procesar.

Flujo (pasos principales):
1. Configuración de credenciales (carga de `client_id`/`client_secret` desde variables o `SHConfig`).
2. Construcción de query OData para el AOI y rango de fechas.
3. Búsqueda de productos y post-filtrado por fecha/sensado.
4. Descarga de los zips de productos.
5. Extracción de las carpetas `.SAFE` y búsqueda de bandas 10m (B02,B03,B04).
6. Creación del composite RGB y guardado como GeoTIFF (parámetros de compresión y blocking).
7. Registro de resultados en consola.

Entradas:
- Parámetros declarados en la celda de configuración.
- Credenciales en variables de entorno (o archivo `.env`).

Salidas:
- Zips en `sentinel2_complete_tiles/`.
- GeoTIFF composites en `processed_tiles/` con sufijo `_RGB_10m.tiff`.

Notas de seguridad:
- No guardar `client_secret` en el repo. Usar `.env` que esté en `.gitignore`.

---

## 02_CompositeBands.ipynb
Propósito:
- Crear composiciones y combinar bandas de imágenes (por ejemplo, indexación y visualización).

Requisitos:
- `rasterio`, `numpy`, `matplotlib`, `skimage` (opcional), `geopandas` (opcional).

Flujo:
1. Cargar imágenes de entrada (TIFF/JP2).
2. Seleccionar bandas y reescalar/normalizar.
3. Aplicar índices (NDVI, EVI, etc.) si está implementado.
4. Guardar composiciones en `Imagenes/` o carpeta `processed_tiles/`.

Entradas/Salidas:
- Entradas: imágenes multibanda.
- Salidas: TIFF compositos y visualizaciones.

---

## 03_Merge_Escenes.ipynb
Propósito:
- Unir varias escenas/tiles en un mosaico o imagen continua.

Requisitos:
- `rasterio.merge`, `gdal`, `numpy`.

Flujo:
1. Listar archivos de entrada.
2. Usar `rasterio.merge.merge` o `gdalwarp` para unir.
3. Reproyectar si es necesario.
4. Guardar resultado en `Imagenes/` o `GeoDatos/`.

Entradas/Salidas:
- Entradas: múltiples tiles.
- Salidas: mosaico TIFF.

---

## 04_Clip_ZonaAgricola.ipynb
Propósito:
- Recortar imágenes/mosaicos a la zona agrícola de interés.

Requisitos:
- `rasterio`, `shapely`, `geopandas`.

Flujo:
1. Cargar AOI desde shapefile o coordenadas.
2. Recortar TIFF usando máscara y transformar.
3. Guardar archivo recortado en `Imagenes/`.

---

## 05_Tile_Mosaics.ipynb
Propósito:
- Dividir mosaicos grandes en tiles más pequeños para procesamiento (por ejemplo, entrenamiento de modelos).

Requisitos:
- `rasterio`, `numpy`.

Flujo:
1. Definir tamaño de tile (por ejemplo 512x512 píxeles).
2. Iterar sobre la imagen y exportar tiles con nombres estandarizados.
3. Opcional: guardar máscaras y metadatos.

Salidas:
- Carpeta de tiles lista para anotación o inferencia.

---

## 06_Calculate_index.ipynb
Propósito:
- Calcular índices espectrales (NDVI, NDWI, EVI, etc.) sobre imágenes o tiles.

Requisitos:
- `rasterio`, `numpy`, `pandas`.

Flujo:
1. Cargar bandas necesarias.
2. Calcular índice con manejo de división por cero y valores saturados.
3. Guardar índice como raster y valores estadísticos en CSV.

---

## 07_FAST_CNN.ipynb
Propósito:
- Entrenar una red neuronal (p. ej. Faster R-CNN u otra) sobre el dataset de silos.

Requisitos:
- `torch`, `torchvision`, `albumentations`, `pycocotools` (según el framework usado).

Flujo general:
1. Preparar dataset y dataloaders (train/val/test).
2. Configurar modelo preentrenado y ajustar capas.
3. Entrenar y guardar pesos en `Nootebooks/pesos/`.
4. Guardar predicciones en `training_output/predictions/`.

---

## 07_FAST_CNNv2_dataagumentation.ipynb
Propósito:
- Versión mejorada del entrenamiento con aumentos de datos.

Requisitos:
- `albumentations`, `torch`.

Flujo:
- Definición de pipeline de aumentos, generación de lotes aumentados y reentrenamiento.

---

## 07_FAST_CNNv2_dataagumentationv2.ipynb
Propósito:
- Iteración adicional con más estrategias de augmentación y balanceo de dataset.

---

## 08_mAP.ipynb
Propósito:
- Calcular métricas de detección (mAP, precision/recall) para los modelos entrenados.

Requisitos:
- `pycocotools` o funciones custom para cálculo de mAP.

Flujo:
1. Cargar predicciones y ground-truth.
2. Calcular mAP y curvas PR.
3. Guardar resultados y visualizaciones.

---

## 09_CLEAN_DATASET.ipynb
Propósito:
- Limpieza y normalización del dataset: etiquetas, tamaños, formato COCO/PASCAL, etc.

Flujo:
1. Validar anotaciones.
2. Eliminar o corregir imágenes corruptas.
3. Exportar dataset limpio para entrenamiento.

---

## Otros archivos relevantes
- `silos_dataset.csv`: catálogo de imágenes y metadatos.
- `pesos/`: pesos entrenados grandes (NO subir al repo; agregar en .gitignore).
- `training_output/`: salidas de inferencia (predicciones) y archivos derivados.

---

## Recomendaciones generales
- Agregar un `.env` en la raíz con claves sensibles y asegurarse de que `.gitignore` incluya `.env`, `*.tiff`, `pesos/`, `training_output/`, y otros archivos grandes.
- Añadir instrucciones de instalación rápidas al inicio de cada notebook (pip install -r requirements.txt) o mantener un `requirements.txt`.
- Mantener rutas relativas para que las notebooks funcionen en diferentes equipos.

---

## Contacto
Para cambios o preguntas sobre la documentación, edita este archivo directamente y haz un commit explicativo.
