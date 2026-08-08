"""
Genera la columna 'Incluir_en_V5' sobre el seguimiento de GT.

Estrategia BALANCEADA:
- Target = TARGET_PER_STRATUM imágenes por cada uno de los 18 strata
- Para strata con suficientes DONE (2020): selecciona TARGET_PER_STRATUM aleatorios; 
  el resto queda en Reserva (uso posterior: test set, respaldo, análisis temporal)
- Para strata sin DONE: selecciona TARGET_PER_STRATUM Pendientes a corregir
- Resultado: 216 imágenes balanceadas en V5, 54 corregidas en Reserva (no se tira nada)
"""

import pandas as pd
import numpy as np

# === CONFIGURACIÓN ===
INPUT_TSV = "seguimiento_gt.tsv"
OUTPUT_CSV = "seguimiento_gt_v5_balanced.csv"
TARGET_PER_STRATUM = 12  # Balanceado: mismo número en cada strata
SEED = 456  # Consistente con tu V4 stratified sampling

# === CARGA Y PREP ===
df = pd.read_csv(INPUT_TSV, sep='\t')
df['stratum'] = df['Año'].astype(str) + '-' + df['Mes'].astype(str).str.zfill(2)

# === NUEVA COLUMNA: 'Asignacion' con tres valores ===
# - 'V5_train'   → entra al training set de V5
# - 'Reserva'    → corregida pero no usada en V5 (candidata a test set / respaldo)
# - 'NoIncluir'  → pendiente, no se corrige por ahora
df['Asignacion'] = 'NoIncluir'

# También mantenemos la columna booleana simple para tu pipeline
df['Incluir_en_V5'] = False

rng = np.random.default_rng(SEED)

for stratum, group in df.groupby('stratum'):
    done_idx = group[group['Estado'] == 'DONE'].index.tolist()
    pend_idx = group[group['Estado'] == 'Pendiente'].index.tolist()
    
    n_done = len(done_idx)
    
    if n_done >= TARGET_PER_STRATUM:
        # Strata con DONE suficientes (ej: 2020): elegir 12 random, resto a Reserva
        selected = rng.choice(done_idx, size=TARGET_PER_STRATUM, replace=False)
        df.loc[selected, 'Asignacion'] = 'V5_train'
        
        # Las DONE no seleccionadas van a Reserva
        no_seleccionados = set(done_idx) - set(selected.tolist())
        df.loc[list(no_seleccionados), 'Asignacion'] = 'Reserva'
    else:
        # Strata con pocas o cero DONE: tomar todas las DONE + completar con Pendientes
        if n_done > 0:
            df.loc[done_idx, 'Asignacion'] = 'V5_train'
        
        gap = TARGET_PER_STRATUM - n_done
        n_select = min(gap, len(pend_idx))
        
        if n_select > 0:
            selected_pend = rng.choice(pend_idx, size=n_select, replace=False)
            df.loc[selected_pend, 'Asignacion'] = 'V5_train'

# Sincronizar la columna booleana
df['Incluir_en_V5'] = (df['Asignacion'] == 'V5_train')

# === RESUMEN ===
print("=" * 70)
print(f"TOTAL imágenes en tabla: {len(df)}")
print()
print("Asignación:")
for cat in ['V5_train', 'Reserva', 'NoIncluir']:
    n = (df['Asignacion'] == cat).sum()
    print(f"  → {cat:12s}: {n}")
print("=" * 70)

print("\nDistribución por strata (V5_train):")
print("-" * 70)
resumen = df[df['Asignacion'] == 'V5_train'].groupby('stratum').agg(
    total_v5=('ID_Imagen', 'count'),
    ya_done=('Estado', lambda x: (x == 'DONE').sum()),
    a_corregir=('Estado', lambda x: (x == 'Pendiente').sum())
).reset_index()
print(resumen.to_string(index=False))

print(f"\n>>> TOTAL V5_train: {resumen['total_v5'].sum()}")
print(f">>> A corregir aún: {resumen['a_corregir'].sum()}")
print(f">>> Reserva (corregidas, alto valor): {(df['Asignacion'] == 'Reserva').sum()}")

# === GUARDAR ===
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n>>> Guardado en: {OUTPUT_CSV}")
print(">>> Filtros sugeridos:")
print("    - Train V5:  Asignacion == 'V5_train' AND Estado == 'DONE'")
print("    - Test extra: Asignacion == 'Reserva'  (ya están corregidas)")
print("    - Por corregir: Asignacion == 'V5_train' AND Estado == 'Pendiente'")
