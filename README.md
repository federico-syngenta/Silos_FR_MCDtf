# Silos_FR_MCDtf

Este proyecto forma parte de la tesis final de la Maestría en Data Science de la universidad Austral sede Rosario y está enfocado en el análisis y procesamiento de imágenes satelitales georreferenciadas "Seninel 2A" de la empresa euorpea para la deteccion y medicion de silos para una region particular de la Argentina. El objetivo principal es aplicar técnicas de procesamiento de imágenes para extraer información relevante que apoye la toma de decisiones en el ámbito agrícola.

## Estructura del Proyecto

- **01_doc/**: Documentación relevante, presentaciones, instructivos y plantillas utilizadas en el desarrollo del proyecto.
- **Imagenes/**: Imágenes georreferenciadas procesadas y crudas utilizadas para el análisis.
- **Nootebooks/**: Notebooks de Jupyter con el desarrollo de los análisis, procesamiento de datos y experimentos realizados.

## Objetivos
- Generar una descarga y repositorio de imagenes del 2020 al 2025 
- Procesar imágenes y aplicar técnicas de limpieza.
- Etiquetar imagenes para la generacion de un set de datos de entrenamiento
- Entrenar un modelo de red neuronal
- Generar visualizaciones y reportes para la toma de decisiones.

## Requisitos
- Python 3.x
- Jupyter Notebook
- Bibliotecas para procesamiento de imágenes y análisis de datos (por ejemplo: numpy, pandas, matplotlib, rasterio, scikit-image, etc.)

## Uso
1. Clonar el repositorio.
2. Instalar los requisitos necesarios.
3. Ejecutar los notebooks en la carpeta `Nootebooks/` para reproducir los análisis.

## Autor
Federico (Syngenta)

## Licencia
Uso académico y de investigación.

## Meetings , progess y proximos pasos
Reunion Gonza Sad 20/08/2025
- Averiguar estado del arte en publicaciones para la deteccion automatica o la segmentacion de imagenes para la deteccion de silo bolsa especificamente (o no)
- Compartir Repo a Gonza y Generar una carpeta drive con toda la documentacion
- Comenzar el pre proyect plan
- Generar segmentacion de espacio tiempo, es decir, definir las imagenes que utilizaremos para generar la biblioteca o la base de datos seleccionando los años, meses de estudio y la superficie

## Ideas
- Utilizar capas de corte que permitan dejar de lado toda area que no sea rural, ejemplo (Pedir capas de soja y maiz de algun año y utilizar eso para extraer la info mas importante)

## links
- Mapa de cobertura de suelos INTA (https://argentina.mapbiomas.org/mapas-de-la-coleccion/)