# Validación temporal 2026 — Resumen completo para la tesis

> Documento de trabajo para incorporar a la tesis. Reúne métodos, parámetros, resultados y limitaciones de la validación temporal con imágenes Sentinel-2 de 2026 (junio, julio y agosto), más el análisis del offset radiométrico L2A.
> Decimales con punto, tal como los produce el código. Versión final: 14/09/2026, test de **29 teselas y 802 silobolsas**.
> Notebooks: `Nootebooks/2026/PIPELINE_2026_all_in_one.ipynb` (principal) y `Nootebooks/2026/PIPELINE_2026_HNK_junjul.ipynb` (corrida complementaria de 20HNK).

---

## 1. Objetivo y etapas

Evaluar la generalización temporal de los cuatro modelos de detección de silobolsas (V2, V3, V4 y V5, Faster R-CNN) sobre imágenes de un año **no usado en el entrenamiento** (2026). El área es la zona agrícola del departamento Marcos Juárez (Córdoba).

| Etapa | Fecha | Test | GT |
|---|---|---|---|
| 1. Entrega V1 | 08/08/2026 | 19 teselas de jun/jul (tiles 20HNH y 20HNJ) | 590 |
| 2. Agosto | 13/09/2026 | + 8 teselas de agosto (20HNH, 20HNJ y 20HNK) | 737 |
| 3. Cobertura 20HNK | 14/09/2026 | + 2 teselas de 20HNK de jun/jul | **802** |

Además se verificó y cuantificó el efecto del offset radiométrico de Sentinel-2 L2A (secciones 7 y 6.5).

---

## 2. Datos satelitales

| Ítem | Detalle |
|---|---|
| Sensor / nivel | Sentinel-2 L2A (reflectancia de superficie) |
| Fuente | AWS S3, bucket `sentinel-s2-l2a` |
| Bandas usadas | B02, B03, B04 y B08 a 10 m; SCL a 20 m para la máscara de nubes |
| Tiles MGRS del entrenamiento (2020–2025) | 20HNH, 20HNJ y 20HNK (verificado en los composites) |
| Tiles MGRS del test 2026 | 20HNH, 20HNJ y 20HNK en los tres meses (ver sección 3.2) |
| Área de recorte | `GeoDatos/argentina_Agriculture_MERGE_Marcos_Juarez.shp` (máscara agrícola) |

**Cobertura de la máscara agrícola por tile MGRS.** Es la fracción del área agrícola que intersecta cada tile; los tiles se superponen, por eso la suma supera el 100 %.

| Tile | Fracción del área agrícola |
|---|---|
| 20HNJ | 74.3 % |
| 20HNH | 19.2 % |
| 20HNK | 15.3 % |
| 20HPJ | 6.1 % (no usado en entrenamiento ni en test) |

La franja norte (al norte de la latitud −32.537, northing 6 400 000 en UTM 20S) solo está cubierta por 20HNK.

---

## 3. Procesamiento

### 3.1 Pipeline (idéntico al usado en 2020–2025)

| Etapa | Descripción | Parámetros |
|---|---|---|
| 1. Descarga | Solo los 5 archivos necesarios por escena | B02, B03, B04, B08 (R10m) y SCL (R20m) |
| 2. Composite sin nubes | Apila R, G, B y NIR, y enmascara con SCL remuestreada a 10 m por vecino más cercano | Clases SCL válidas: 4, 5, 6, 7 y 11. Los píxeles no válidos quedan en 0. **Los DN se conservan crudos, sin restar el offset.** |
| 3. Merge | Mosaico por fecha y secuencia (`rasterio.merge`) | Jun/jul: 2 tiles (20976 × 10980 px). Agosto: 3 tiles (30978 × 10980 px). Corrida 20HNK: 1 tile. |
| 4. Clip | Recorte a la máscara agrícola | Fuera de la máscara = NaN (float32) |
| 5. Tiling | Teselas de 1024 × 1024 px (≈10.24 × 10.24 km) | 20 % de solapamiento. Se conserva una tesela si tiene ≥20 % de píxeles válidos y <80 % de píxeles oscuros. |
| 6. Índice y candidatos | INBNV = ((G + R) − NIR) / ((G + R) + NIR). Umbral por percentil en cada tesela, componentes conexas, dilatación y vectorización. | Percentil 99.8, regiones de más de 3 píxeles, dilatación de 1 píxel → `_PERCENTILE_POLYGONS.shp` |

### 3.2 Corridas 2026

| Corrida | Tiles MGRS | Fechas | Escenas | Mosaicos | Teselas | Tiempo de CPU |
|---|---|---|---|---|---|---|
| Jun/jul (principal) | 20HNH + 20HNJ | 02/06 al 24/07 | — | 28 | 1176 (796 de junio y 380 de julio) | — |
| Agosto | 20HNH + 20HNJ + 20HNK | 01/08 al 31/08 | 48 | 17 | 980 | ≈6 h |
| 20HNK jun/jul (complementaria) | 20HNK | 01/06 al 24/07 (mismas fechas que la principal) | 30 | 30 | 257 (149 enteras en la franja norte) | ≈3.5 h |

La corrida complementaria de 20HNK se procesó en una carpeta propia, con el mismo pipeline y los mismos parámetros. Sus mosaicos y teselas llevan el sufijo `_HNK` (por ejemplo `2026_6_19_0_HNK_tile_r05_c04.tif`) para no chocar con la grilla de la corrida principal. Así, las 19 teselas ya curadas no se modificaron.

**Agosto por fecha:**

| Fecha | Teselas |
|---|---|
| 01/08 | 142 |
| 06/08 | 46 |
| 08/08 | 146 |
| 16/08 (seq 0) | 49 |
| 16/08 (seq 1) | 29 |
| 18/08 | 30 |
| 20/08 | 145 |
| 21/08 (seq 0) | 53 |
| 21/08 (seq 1) | 60 |
| 23/08 | 138 |
| 26/08 | 4 |
| 28/08 | 138 |

Las fechas 03, 11, 13 y 31 de agosto no produjeron teselas por nubosidad.

---

## 4. Conjunto de test y ground truth

### 4.1 Selección de teselas

- **Jun/jul, corrida principal (19 teselas):**
  - 15 se sortearon estratificadas por mes, con semilla 456: 8 de junio y 7 de julio.
  - Otras 4, curadas antes (21/06/2026), completan las 19: `2026_6_14_0_tile_r07_c02`, `2026_6_14_1_tile_r11_c05`, `2026_6_19_0_tile_r09_c04` y `2026_7_24_0_tile_r11_c03`. **[COMPLETAR POR EL AUTOR: criterio de selección de estas 4.]**
- **Agosto (8 teselas):** se sortearon entre las 980, con semilla 464 (456 + mes). No se reemplazó ninguna a criterio visual.
- **20HNK jun/jul (2 teselas):**
  - Una de junio y una de julio, sorteadas con semilla 456 + mes (462 y 463).
  - Solo entraron al sorteo teselas que cumplían tres criterios: estar **100 % en la franja norte** (cubierta solo por 20HNK), tener **≥70 % de píxeles válidos** y tener **≤1 % de píxeles enmascarados por nube**.
  - Cumplían los criterios 17 teselas de junio y 5 de julio. Salieron `2026_6_19_0_HNK_tile_r05_c04` y `2026_7_9_0_HNK_tile_r05_c06`, que no se superponen entre sí.
  - Hay que declararlo: la selección de estas 2 fue dirigida por cobertura (completar el tile faltante) y aplicó un filtro de calidad que las demás teselas no tuvieron.

**Composición final: 29 teselas.**

| Mes | Teselas | GT |
|---|---|---|
| Junio | 12 (11 + 1 de 20HNK) | 389 |
| Julio | 9 (8 + 1 de 20HNK) | 266 |
| Agosto | 8 | 147 |
| **Total** | **29** | **802** |

**Representación de la franja norte:**

| | Universo | Test |
|---|---|---|
| Jun/jul | 149 de 1325 teselas (11.2 %) | 2 de 21 (9.5 %) |
| Agosto | 111 de 980 (11.3 %) | 1 de 8 (12.5 %) |

En los dos períodos, el test muestrea el norte en proporción similar a su peso en el territorio.

### 4.2 Ground truth semiautomático

1. Se generan candidatos con INBNV (etapa 6).
2. Se curan a mano en QGIS: se eliminan los falsos positivos y se digitalizan las silobolsas faltantes.
3. El GT se guarda en `<tesela>_PERCENTILE_POLYGONS.shp`.
4. Para evaluar, cada polígono se convierte en su caja envolvente en píxeles.

**Qué parte de los candidatos del índice terminó como GT:**

| Teselas | Candidatos | GT curado | Proporción |
|---|---|---|---|
| Agosto | 425 | 147 | 34.6 % |
| 20HNK jun/jul | 164 | 65 | 39.6 % |

### 4.3 GT por tesela y detecciones de V5

Las detecciones de V5 se cuentan después del umbral de 0.5 y del NMS.

| Tesela | Mes | Candidatos INBNV | GT curado | Detecciones V5 |
|---|---|---|---|---|
| 2026_6_11_0_tile_r14_c05 | Jun | – | 0 | 0 |
| 2026_6_14_0_tile_r07_c02 | Jun | – | 28 | 20 |
| 2026_6_14_1_tile_r09_c01 | Jun | – | 12 | 13 |
| 2026_6_14_1_tile_r11_c05 | Jun | – | 63 | 62 |
| 2026_6_19_0_tile_r03_c09 | Jun | – | 57 | 51 |
| 2026_6_19_0_tile_r07_c10 | Jun | – | 11 | 12 |
| 2026_6_19_0_tile_r09_c01 | Jun | – | 14 | 12 |
| 2026_6_19_0_tile_r09_c04 | Jun | – | 57 | 55 |
| 2026_6_22_0_tile_r13_c04 | Jun | – | 59 | 53 |
| 2026_6_27_0_tile_r02_c04 | Jun | – | 30 | 29 |
| 2026_6_29_0_tile_r16_c02 | Jun | – | 23 | 26 |
| **2026_6_19_0_HNK_tile_r05_c04** | Jun | 77 | 35 | 34 |
| 2026_7_2_0_tile_r09_c02 | Jul | – | 35 | 35 |
| 2026_7_2_0_tile_r13_c04 | Jul | – | 52 | 48 |
| 2026_7_2_0_tile_r17_c01 | Jul | – | 19 | 18 |
| 2026_7_9_0_tile_r13_c03 | Jul | – | 43 | 37 |
| 2026_7_17_0_tile_r08_c05 | Jul | – | 37 | 31 |
| 2026_7_24_0_tile_r10_c04 | Jul | – | 16 | 22 |
| 2026_7_24_0_tile_r11_c03 | Jul | – | 27 | 29 |
| 2026_7_24_1_tile_r12_c03 | Jul | – | 7 | 15 |
| **2026_7_9_0_HNK_tile_r05_c06** | Jul | 87 | 30 | 27 |
| 2026_8_1_0_tile_r23_c03 | Ago | 55 | 25 | 28 |
| 2026_8_8_0_tile_r08_c09 | Ago | 56 | 16 | 17 |
| 2026_8_8_0_tile_r10_c09 | Ago | 57 | 45 | 41 |
| 2026_8_16_1_tile_r00_c01 | Ago | 22 | 2 | 6 |
| 2026_8_18_0_tile_r24_c01 | Ago | 17 | 10 | 13 |
| **2026_8_21_0_tile_r03_c08** (franja norte) | Ago | 18 | 0 | 2 |
| 2026_8_21_0_tile_r10_c10 | Ago | 80 | 4 | 4 |
| 2026_8_28_0_tile_r13_c04 | Ago | 60 | 45 | 46 |
| **Total** | | | **802** | **786** |

En negrita, las 3 teselas de la franja norte.

**Observaciones de calidad de imagen:**
- **`2026_8_21_0_tile_r10_c10`:** tiene bruma que SCL no eliminó.
- **`2026_7_9_0_HNK_tile_r05_c06`:** tiene nubes pequeñas sin enmascarar en la esquina superior izquierda. Los candidatos de esa zona se eliminaron en la curación.
- **`2026_8_16_1_tile_r00_c01`:** tiene abundantes cuerpos de agua.

---

## 5. Protocolo de evaluación

| Parámetro | Valor |
|---|---|
| Arquitectura | Faster R-CNN ResNet50-FPN, 2 clases. Anchors de 16, 32, 64, 128 y 256 px; relaciones de aspecto 0.2, 0.5, 1, 2 y 5. |
| Modelos | V2 (`modelo_silos_v2_optimizado.pth`), V3 (`modelo_silos_v3_aug.pth`), V4 (`modelo_silos_v4_10k.pth`) y V5 (`modelo_silos_v5_FINAL.pth`) |
| Entrada | Solo RGB (bandas 1–3). NaN → 0, división por 10000 y recorte a [0, 1]. Es el mismo preprocesamiento del entrenamiento (verificado en los notebooks 07, 10 y 10b). |
| Umbral de confianza | 0.5 |
| Deduplicación | NMS post-hoc con IoU de 0.3, igual para todos los modelos |
| Criterio de acierto | IoU ≥ 0.15, con emparejamiento greedy por score |
| AP@0.15 | Interpolado en 11 puntos, sobre las detecciones con score ≥ 0.5 y después del NMS |
| Wilcoxon | Pareado, sobre los falsos positivos por imagen (umbral de 0.5 y NMS) |
| Bootstrap de AP | Pareado por imagen: 2000 remuestreos, semilla 0, AP de 11 puntos con la curva completa (sin umbral ni NMS) |
| Sensibilidad al offset | V4 y V5 evaluados dos veces sobre las 29 teselas: con el preprocesamiento original y restando 1000 a los DN antes de dividir por 10000. Se comparan con los mismos tests pareados. |
| Hardware | CPU. Validación: ≈25 min. Sensibilidad: ≈17 min. |

---

## 6. Resultados

### 6.1 Métricas globales: 29 teselas, 802 objetos de GT

| Modelo | TP | FP | FN | Predicciones | Precisión | Recall | F1 | AP@0.15 |
|---|---|---|---|---|---|---|---|---|
| V2 | 603 | 274 | 199 | 877 | 0.6876 | 0.7519 | 0.7183 | 0.6943 |
| V3 | 517 | 98 | 285 | 615 | 0.8407 | 0.6446 | 0.7297 | 0.6115 |
| V4 | 579 | 161 | 223 | 740 | 0.7824 | 0.7219 | 0.7510 | 0.6874 |
| **V5** | **636** | **150** | **166** | **786** | **0.8092** | **0.7930** | **0.8010** | **0.7048** |

### 6.2 Estabilidad al ampliar el test

| Modelo | F1 con 19 teselas | F1 con 27 | F1 con 29 | AP con 19 | AP con 27 | AP con 29 |
|---|---|---|---|---|---|---|
| V2 | 0.743 | 0.717 | 0.718 | 0.707 | 0.692 | 0.694 |
| V3 | 0.746 | 0.728 | 0.730 | 0.619 | 0.609 | 0.612 |
| V4 | 0.776 | 0.751 | 0.751 | 0.707 | 0.687 | 0.687 |
| V5 | 0.808 | 0.796 | 0.801 | 0.709 | 0.704 | 0.705 |

El orden de los modelos se mantiene en las tres versiones del test.

### 6.3 Desempeño por período

Se obtiene por diferencia entre corridas. Es válido porque TP, FP y FN son aditivos por imagen, las teselas comunes son idénticas (verificado por hash) y la inferencia es determinística. El AP por período no puede obtenerse así.

**Jun/jul: 21 teselas, 655 objetos de GT.**

| Modelo | TP | FP | FN | Precisión | Recall | F1 |
|---|---|---|---|---|---|---|
| V2 | 503 | 198 | 152 | 0.718 | 0.768 | 0.742 |
| V3 | 433 | 73 | 222 | 0.856 | 0.661 | 0.746 |
| V4 | 484 | 113 | 171 | 0.811 | 0.739 | 0.773 |
| **V5** | **522** | **107** | **133** | **0.830** | **0.797** | **0.813** |

**Agosto: 8 teselas, 147 objetos de GT.** La última columna excluye la única tesela de la franja norte (`2026_8_21_0_tile_r03_c08`, GT = 0).

| Modelo | TP | FP | FN | Precisión | Recall | F1 | F1 sin la tesela norte |
|---|---|---|---|---|---|---|---|
| V2 | 100 | 76 | 47 | 0.568 | 0.680 | 0.619 | 0.649 |
| V3 | 84 | 25 | 63 | 0.771 | 0.571 | 0.656 | 0.667 |
| V4 | 95 | 48 | 52 | 0.664 | 0.646 | 0.655 | 0.681 |
| **V5** | **114** | **43** | **33** | **0.726** | **0.776** | **0.750** | **0.755** |

**Las 2 teselas de 20HNK de jun/jul (65 objetos de GT):**

| Modelo | TP | FP | FN |
|---|---|---|---|
| V2 | 47 | 16 | 18 |
| V3 | 39 | 0 | 26 |
| V4 | 45 | 10 | 20 |
| V5 | 54 | 7 | 11 |

**Lectura:**
- **Agosto es el período más difícil.** El F1 cae de jun/jul a agosto en todos los modelos: 0.123 en V2, 0.090 en V3, 0.118 en V4 y **0.063 en V5**, que es el más robusto. La caída viene sobre todo de la precisión.
- **La caída no se explica por geografía.** Sin la única tesela de agosto de la franja norte, la caída se mantiene casi entera (V5 0.755 frente a 0.813 en jun/jul). Además, jun/jul también incluye teselas del norte.
- **Los valores de agosto son indicativos:** son 8 teselas, e incluyen una con bruma y otra sin silobolsas.

### 6.4 Significancia estadística (V3 excluido de las comparaciones)

**Falsos positivos por imagen (Wilcoxon pareado).** La mediana de la diferencia es la de 29 teselas.

| Comparación | Mediana de la diferencia | p (19 teselas) | p (27) | p (29) |
|---|---|---|---|---|
| V5 vs V4 | +1.0 | 0.2215 | 0.4544 | 0.5562 |
| V5 vs V2 | −2.0 | 0.0144 | 0.0008 | **0.0005** |
| V4 vs V2 | −4.0 | 0.0156 | 0.0022 | **0.0023** |

**AP con la curva completa (bootstrap pareado, 2000 remuestreos).** La diferencia y el IC son los de 29 teselas.

| Comparación | Diferencia | IC95 % | p (19) | p (27) | p (29) |
|---|---|---|---|---|---|
| V5 − V4 | +0.046 | [+0.007, +0.080] | 0.432 | 0.056 | **0.025** |
| V5 − V2 | +0.057 | [+0.022, +0.084] | 0.090 | 0.004 | **< 0.001** |
| V4 − V2 | +0.011 | [−0.014, +0.034] | 0.158 | 0.320 | 0.328 |

El p < 0.001 significa que ningún remuestreo dio una diferencia a favor de V2.

**Lectura:**
- **V5 supera a V2 con significancia robusta:** tiene menos falsos positivos por imagen (p = 0.0005) y mayor AP (p < 0.001). Ambos resultados resisten una corrección de Bonferroni para 3 comparaciones (α = 0.0167).
- **V4 reduce los falsos positivos respecto de V2** (p = 0.002), pero sin mejora de AP.
- **V5 frente a V4:** el AP favorece a V5 (+0.046, IC95 % que excluye el 0, p ≈ 0.025), pero **no resiste Bonferroni**. En falsos positivos no hay diferencia. Conviene redactarlo como una ventaja consistente en AP, con significancia marginal. El tamaño del test se fijó por criterios de cobertura antes de ver estos resultados.

### 6.5 Sensibilidad al offset L2A (V4 y V5, 29 teselas)

| Modelo | Offset restado | TP | FP | FN | Precisión | Recall | F1 | AP@0.15 |
|---|---|---|---|---|---|---|---|---|
| V4 | 0 (original) | 579 | 161 | 223 | 0.7824 | 0.7219 | 0.7510 | 0.6874 |
| V4 | 1000 | 632 | 215 | 170 | 0.7462 | 0.7880 | 0.7665 | 0.6991 |
| V5 | 0 (original) | 636 | 150 | 166 | 0.8092 | 0.7930 | 0.8010 | 0.7048 |
| V5 | 1000 | 673 | 167 | 129 | 0.8012 | 0.8392 | 0.8197 | 0.7857 |

**Efecto de restar el offset**, medido como corregido menos original y pareado por imagen:

| Modelo | FP por imagen (mediana) | Wilcoxon p | Δ AP, curva completa | IC95 % | p |
|---|---|---|---|---|---|
| V4 | +1.0 | 0.0086 | +0.058 | [+0.025, +0.079] | < 0.001 |
| V5 | 0.0 | 0.2854 | +0.038 | [+0.026, +0.073] | < 0.001 |

**Lectura:**
- **Los modelos no son insensibles al corrimiento.** Llevar las imágenes de 2026 a la escala de 2020–2021 **mejora el AP de ambos modelos de forma significativa**, sobre todo por un aumento del recall. En V4, el recall pasa de 0.722 a 0.788 y el AP@0.15 sube +0.012. En V5, el recall pasa de 0.793 a 0.839 y el AP@0.15 sube +0.081.
- **En V4, la corrección también aumenta los falsos positivos** (p = 0.009). En V5, los falsos positivos no cambian (p = 0.29): V5 es más estable en precisión.
- **Consecuencia 1: las métricas reportadas con el pipeline original son conservadoras.** El desempeño 2026 está, en todo caso, subestimado.
- **Consecuencia 2: el orden V5 > V4 se mantiene en las dos escalas** (F1 0.820 contra 0.767; AP 0.786 contra 0.699). La comparación central no depende del offset.
- **Alcance:** este análisis mide la sensibilidad de los modelos ya entrenados a un corrimiento radiométrico de 0.1 en la escala [0, 1]. **No mide el efecto de corregir todo el pipeline** (entrenamiento y test), y no permite afirmar cuál sería el desempeño en ese caso. Tampoco permite determinar por qué la escala 2020–2021 favorece a los modelos.

### 6.6 Figura

`D:\Silos\Base_2026\validacion_2026.png` muestra una grilla de 6 columnas con las 29 teselas: GT en verde y V5 en rojo, con su score. Las versiones anteriores están en `validacion_2026_jun-jul.png` (19 teselas) y `validacion_2026_27teselas.png`.

---

## 7. Verificación del offset radiométrico L2A (BOA_ADD_OFFSET)

Desde el baseline de procesamiento 04.00 de ESA (enero de 2022), los productos L2A incluyen un offset de −1000 declarado en los metadatos, que debe restarse a los DN. El bucket de AWS distribuye los DN sin aplicarlo. **Ni el pipeline ni los notebooks de entrenamiento (07, 10 y 10b) lo restan**: todos dividen los DN por 10000.

**Evidencia.** Banda B04 de los composites, tile 20HNJ, todas las escenas de julio de cada año, píxeles > 0:

| Año | Escenas | p0.1 | p1 | p5 | p50 | Mínimo |
|---|---|---|---|---|---|---|
| 2020 | 22 | 95 | 404 | 747 | 1728 | 1 |
| 2021 | 24 | 43 | 303 | 651 | 1738 | 1 |
| 2022 | 12 | 1248 | 1456 | 1752 | 2340 | 1085 |
| 2023 | 13 | 1222 | 1338 | 1545 | 2114 | 778 |
| 2024 | 12 | 1192 | 1385 | 1692 | 2288 | 907 |
| 2025 | 15 | 1181 | 1352 | 1593 | 2146 | 595 |
| 2026 | 13 | 1197 | 1360 | 1603 | 2236 | 961 |

Los percentiles bajos (píxeles oscuros, como el agua) saltan de 40–400 a 1200–1450 exactamente en 2022 y se mantienen estables después. Es la firma del offset.

**Implicancias:**
- El entrenamiento de V5 mezcló las dos escalas sin corregir: 216 imágenes, 12 por cada combinación de año (2020–2025) y mes (jun, jul, ago). **72 no tienen offset (2020–2021) y 144 sí (2022–2025).**
- El test 2026 está en la escala con offset, la misma de dos tercios del entrenamiento.
- V2, V3, V4 y V5 comparten el mismo preprocesamiento sin corregir. Por eso el offset es una condición constante del experimento, no una variable que distinga entre modelos.
- El análisis de sensibilidad (6.5) cuantifica el efecto: corregirlo en el test mejora el AP entre +0.04 y +0.06 (curva completa), sin alterar el orden de los modelos.

---

## 8. Hallazgos clave (para la discusión)

1. **V5 es el mejor modelo en el año no visto:** F1 = 0.801, precisión = 0.809, recall = 0.793 y AP@0.15 = 0.705, sobre 29 teselas y 802 silobolsas. Los tres meses cubren los tres tiles MGRS.
2. **V5 supera a V2 con significancia robusta**, en falsos positivos por imagen y en AP, y resiste Bonferroni. Frente a V4, la ventaja en AP es consistente pero de significancia marginal: p ≈ 0.025, sin corrección.
3. **La generalización temporal se sostiene pero se degrada en agosto.** El F1 de V5 pasa de 0.813 en jun/jul a 0.750 en agosto, y V5 es el que menos cae. La caída no se explica por la cobertura geográfica.
4. **Hay un compromiso entre precisión y recall entre versiones.** V3 es el más preciso (0.84) pero el que menos detecta (recall 0.64). V2 detecta mucho, pero con muchos falsos positivos. V5 logra el mejor equilibrio.
5. **El offset L2A no corregido tiene un efecto medible pero no altera las conclusiones.** Las métricas reportadas son conservadoras y el orden de los modelos se mantiene. Corregirlo en todo el pipeline es un trabajo futuro concreto.
6. **El índice INBNV solo no alcanza como detector.** Entre el 35 % y el 40 % de sus candidatos terminaron como GT, lo que justifica el aprendizaje profundo.

---

## 9. Limitaciones y amenazas a la validez

- **Tamaño de muestra:** son 29 teselas y 802 objetos. Las métricas por período, sobre todo las de agosto con 8 teselas, son indicativas.
- **Anotación:** el GT es semiautomático (candidatos INBNV) y lo curó un único anotador. Pueden faltar silobolsas que el índice no propuso.
- **Criterio de acierto permisivo:** IoU = 0.15, por el tamaño pequeño de los objetos a 10 m.
- **No independencia espacial:** algunas teselas cubren la misma zona en fechas distintas (por ejemplo, `r13_c04` el 22/06 y el 02/07, o `r09_c01` el 14/06 y el 19/06), así que las imágenes no son del todo independientes para los tests estadísticos.
- **Selección heterogénea:** las 2 teselas de 20HNK de jun/jul se sortearon con un filtro de calidad (≥70 % de píxeles válidos, sin nubes) y dirigido por cobertura, que no se aplicó al resto del test. Además provienen de una corrida separada, con el mismo pipeline y parámetros.
- **Comparaciones múltiples:** con 3 comparaciones por test, solo las diferencias con p < 0.0167 resisten Bonferroni. V5 − V4 en AP (p ≈ 0.025) no lo resiste.
- **Offset L2A:** no está corregido en entrenamiento ni en test. Su efecto está cuantificado en la sección 6.5, pero no se evaluó el reentrenamiento con escala homogénea.
- **Máscara de nubes imperfecta:** SCL no elimina la bruma ni las nubes pequeñas. Hay dos teselas afectadas: `8_21_0_r10_c10` y `7_9_0_HNK_r05_c06`.
- **Solo RGB:** los modelos descartan el NIR disponible.
- **Tile 20HPJ:** cubre el 6 % del área agrícola y no se usó ni en entrenamiento ni en test.

**Trabajo futuro sugerido:** restar el offset en todo el pipeline para las imágenes posteriores a enero de 2022 (o usar productos armonizados), reentrenar y reevaluar. La sensibilidad medida justifica hacerlo: +0.04 a +0.06 de AP con la curva completa y hasta +0.08 de AP@0.15 (V5).

---

## 10. Trazabilidad

**Archivos (`D:\Silos\Base_2026\`):**

| Archivo | Contenido |
|---|---|
| `resultados_2026.csv` | Métricas finales (29 teselas) |
| `resultados_2026_27teselas.csv` | Versión intermedia (27 teselas) |
| `resultados_2026_jun-jul.csv` | Entrega V1 (19 teselas) |
| `sensibilidad_offset_2026.csv` | V4 y V5, original y restando 1000 |
| `validacion_2026.png` | Figura con 29 teselas |
| `validacion_2026_27teselas.png` | Figura intermedia (27 teselas) |
| `validacion_2026_jun-jul.png` | Figura de V1 |
| `Pred_2026_Compare\` | Shapefiles de GT y de predicciones por modelo (con score), para las 29 teselas |
| `test\` | 29 teselas con GT curado |
| `test_BACKUP_2026-09-13\` | Respaldo del GT de jun/jul (19) |
| `test_BACKUP_2026-09-13_ago_curado\` | Respaldo del GT de 27 teselas |
| `test_BACKUP_2026-09-14_29_curado\` | Respaldo del GT de 29 teselas |

Los datos de la corrida de 20HNK están en `D:\Silos\Base_2026_HNK_junjul\`.

**Cambios en los notebooks.** Cada cambio está marcado con `# [MOD fecha]` sobre la línea modificada.
- **Notebook principal:**
  - Configuración de agosto, con 20HNK, `MESES_A_PROCESAR` y `mes_de()`.
  - Filtro por mes en las etapas 2, 5 y 6.
  - Protección del GT curado.
  - Celda de agosto movida y `N_AGOSTO = 8`.
  - Figura en grilla.
  - `OFFSET_L2A` (vale 0 por defecto, idéntico al original) y la celda de sensibilidad.
- **Notebook de 20HNK:** copia del pipeline con su propia carpeta, solo 20HNK, fechas del 01/06 al 24/07, sufijo `_HNK` y una celda nueva de selección con criterios de calidad.
- **Commit `545ab1c`:** registra el notebook principal con la corrida de agosto y la validación de 27 teselas. Los cambios posteriores (corrida de 20HNK, validación de 29 y sensibilidad) están pendientes de commit.

---

## 11. Pendiente de completar por el autor

- El criterio de selección de las 4 teselas de jun/jul curadas el 21/06/2026 (sección 4.1).
- Una breve descripción de qué distingue a cada modelo (V2 optimizado, V3 con aumentación de datos, V4 con 10k muestras y V5 final): datos, épocas y aumentos.
