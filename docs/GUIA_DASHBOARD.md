# Guía paso a paso: Crear el dashboard en MongoDB Charts

Esta guía explica cómo crear el dashboard de CD Pipeline Analytics desde cero en MongoDB Charts.

---

## Requisitos previos

- Datos ingeridos en Atlas: `platform_analytics.pipeline_events`
- Cuenta MongoDB Atlas con acceso al cluster donde están los datos

---

## Parte 1: Acceder a MongoDB Charts

1. Entra a [MongoDB Atlas](https://cloud.mongodb.com) e inicia sesión.
2. Selecciona tu organización y tu proyecto.
3. En el menú izquierdo, haz clic en **Charts** (debajo de tu nombre de proyecto).
4. Si es la primera vez, Charts te pedirá **conectar un cluster**. Haz clic en **Connect** y selecciona el cluster que tiene la base `platform_analytics`.
5. Una vez conectado, estarás en el listado de dashboards.

---

## Parte 2: Crear Data Sources (orígenes de datos)

En MongoDB Charts, cada gráfico obtiene los datos de un **Data Source**. Hay dos tipos:

- **Collection**: la colección tal cual.
- **Charts View (aggregation)**: resultados de una pipeline de agregación.

Para este dashboard usamos **Charts View** con las pipelines del archivo `scripts/aggregation_pipelines.js`.

### 2.1 Crear el primer Data Source (Deployments por Semana)

1. En Charts, ve al menú **Data Sources**.
2. Clic en **Add Data Source**.
3. Elige **Create Charts View** (no "Use collection").
4. Configura:
   - **Database**: `platform_analytics`
   - **Collection**: `pipeline_events`
   - **Pipeline**: pega el siguiente código (es `view_deployments_by_week`):

```json
[
  { "$match": { "timestamp": { "$exists": true } } },
  { "$match": { "event_type": "deployment" } },
  { "$group": { "_id": { "$dateToString": { "format": "%Y-W%V", "date": "$timestamp" } }, "count": { "$sum": 1 } } },
  { "$sort": { "_id": 1 } }
]
```

5. Clic en **Save**.
6. Pon nombre: `Deployments por Semana`.

### 2.2 Crear el resto de Data Sources

Repite el paso 2.1 para cada uno. Copia la pipeline desde `scripts/aggregation_pipelines.js` y conviértela a JSON (sustituye `null` por `null`, elimina comentarios). O usa directamente el formato de Charts (acepta agregaciones en formato de array de etapas).

| Nombre del Data Source | Pipeline en .js | Campos para el gráfico |
|------------------------|-----------------|------------------------|
| Deployments por Semana | `view_deployments_by_week` | X: _id, Y: count |
| CFR por Región | `view_cfr_by_region` | X: region, Y: cfr_pct |
| Top Failure Reasons | `view_top_failure_reasons` | X: _id, Y: count |
| SLA por Equipo | `view_sla_by_team` | X: team, Y: sla_pct |
| Distribución Trigger | `view_trigger_distribution` | X: _id, Y: count |
| Media móvil 7d | `pipeline_2_rolling_avg_duration` | X: date, Y: rolling_avg_7d |
| Percentiles por Equipo | `pipeline_3_percentiles_by_team` | X: team, Y: p50/p90/p99 |
| Histograma duración | `pipeline_4_duration_histogram_with_failures` | X: range, Y: count |
| Eficiencia por Autor | `pipeline_5_author_efficiency_score` | X: author, Y: efficiency_score |
| Fallos por Environment | `pipeline_6_failure_correlation_analysis` | environment, top_reasons |

**Atajo:** Todas las pipelines en formato JSON están en `docs/pipelines_for_charts.json`. Abre ese archivo y copia el array de cada pipeline para pegarlo en Charts.

---

## Parte 3: Crear el Dashboard

1. Clic en **Dashboards** en el menú izquierdo.
2. Clic en **Create Dashboard**.
3. Pon título: **CD Pipeline Analytics**.

---

## Parte 4: Añadir gráficos al dashboard

Para cada gráfico:

1. En el dashboard, clic en **Add Chart**.
2. Elige el **Data Source** correspondiente (el que creaste en Parte 2).
3. Configura el tipo de gráfico, los ejes, la **agregación** (Sum) y las **series** según la tabla inferior.
4. **Si aparece "count(campo)"**: Customize → Fields → Label Override → activar y escribir "Cantidad" (ver sección más abajo).
5. Clic en **Add Chart** para añadirlo al dashboard.
6. Arrastra y redimensiona el gráfico para organizar el layout.

### Configuración por gráfico

| Gráfico | Data Source | Tipo de chart (MongoDB Charts) | Eje X / Categoría | Eje Y / Valor | Interpretación |
|---------|-------------|-------------------------------|-------------------|---------------|----------------|
| Deployments por Semana | Deployments por Semana | **Line Chart** o **Area Chart** | week | count | Tendencia de deployments en el tiempo. Picos o caídas señalan cambios en la actividad de despliegue. |
| CFR por Región | CFR por Región | **Column Chart** | region | cfr_pct | Change Failure Rate por región. Regiones con barras altas tienen más fallos; objetivo típico &lt; 15%. |
| Top Failure Reasons | Top Failure Reasons | **Bar Chart** | failure_reason | count | Causas más frecuentes de fallo. Prioriza resolver las barras más largas (timeout, test_failure, etc.). |
| SLA por Equipo | SLA por Equipo | **Bar Chart** | team | sla_pct | Porcentaje de eventos que cumplieron SLA por equipo. Barras más largas = mejor cumplimiento. |
| Distribución Trigger | Distribución Trigger | **Donut Chart** | trigger | count | Origen de los disparos: webhook, merge, manual, schedule. Permite ver qué flujos son más usados. |
| Media móvil 7d | Media móvil 7d | **Line Chart** (Discrete) | X: `date` (sin binning) | Y: `rolling_avg_7d` (Sum) | X = fechas; Y = duración suavizada. No usar rolling_avg_7d en X. |
| Percentiles | Percentiles por Equipo | **Bar Chart** (Grouped) | team | p50_seconds, p90_seconds, p99_seconds (3 series) | Latencia P50/P90/P99 por equipo. P99 alto = colas ocasionales lentas que afectan SLO. |
| Histograma duración | Histograma duración | **Column Chart** | range_label | count | Cantidad de pipelines por rango de duración (0-60 s, 60-120 s, etc.). Detecta si la mayoría son rápidas o hay colas largas. |
| Eficiencia por Autor | Eficiencia por Autor | **Bar Chart** | author | efficiency_score | Score combinado de throughput, éxito y coste. Mayor score = autor más eficiente. |
| Fallos por Environment | Fallos por Environment | **Table** | environment | top_reasons | Top 5 causas de fallo por environment. Útil para ver si dev/staging/prod fallan por razones distintas. |

### Agregación en el canal de valor (evitar "count(campo)")

Charts genera labels como "count(failure_reason)" cuando usa agregación **Count** sobre el campo categoría. Como los datos ya vienen agregados por pipeline:

1. En el canal de **valor** (X en Bar Chart, Y en Column/Line, Arc en Donut), al mapear `count`, `cfr_pct`, etc., selecciona **Sum** (no Count).
2. Para campos que son promedios o ratios (`cfr_pct`, `sla_pct`, `rolling_avg_7d`), usa **Sum** o **Mean** según lo que Charts ofrezca.
3. Si sigue mostrando "count(campo)", usa **Label Override** (siguiente sección).

### Label Override para corregir etiquetas

1. Clic en el gráfico → pestaña **Customize**.
2. Expandir **Fields**.
3. Elegir el campo con label incorrecto (ej. el que muestra "count(failure_reason)").
4. Activar **Label Override** (On).
5. Escribir el label deseado, por ejemplo: **Cantidad**, **CFR (%)**, **SLA cumplido (%)**, **Duración media 7d (s)**, **Puntuación eficiencia**.

### Series (donde aplica)

- **Percentiles por Equipo**: mapea los tres campos `p50_seconds`, `p90_seconds`, `p99_seconds` en el canal de valor (X Axis). Charts los tratará como 3 series. Agregación **Sum** o **Mean** para cada uno.
- Los demás gráficos no usan Series.

### Detalle de configuración por gráfico

**Deployments por Semana**  
- Line/Area Chart. X: `week` | Y: `count` (Sum)  
- *Tendencia de deployments en el tiempo.*

**CFR por Región**  
- Column Chart. X: `region` | Y: `cfr_pct` (Sum o Mean)  
- *Change Failure Rate (%). Objetivo &lt; 15%.*

**Top Failure Reasons**  
- Bar Chart. Y: `failure_reason` | X: `count` (**Sum**, no Count)  
- Label Override en `count` → **Cantidad** si aparece "count(failure_reason)".

**SLA por Equipo**  
- Bar Chart. Y: `team` | X: `sla_pct` (Sum o Mean)  
- *% de eventos que cumplieron SLA.*

**Distribución Trigger**  
- Donut Chart. Label: `trigger` | Arc: `count` (**Sum**)  
- Label Override en Arc → **Cantidad** si aparece "count(trigger)".

**Media móvil 7d**  
- Discrete Line Chart. **X Axis: `date`** (categoría temporal; **sin binning**) | **Y Axis: `rolling_avg_7d`** (agregación Sum o Mean)  
- Importante: el eje X debe ser `date`, no `rolling_avg_7d`. Si X tiene binning 350–360, 360–370, está mal (está usando rolling_avg_7d en X). Corrige: X = date, Y = rolling_avg_7d.

**Percentiles por Equipo**  
- Bar Chart (Grouped). Y: `team` | X: `p50_seconds`, `p90_seconds`, `p99_seconds` (3 series, Sum o Mean cada una)  
- *Latencia P50/P90/P99 por equipo.*

**Histograma duración**  
- Column Chart. X: `range_label` | Y: `count` (Sum)  
- *Cantidad de pipelines por rango de duración.*

**Eficiencia por Autor**  
- Bar Chart. Y: `author` | X: `efficiency_score` (Sum o Mean)  
- *Score de eficiencia por autor.*

**Fallos por Environment**  
- Table. Columnas: `environment`, `top_reasons`  
- *Top 5 causas de fallo por environment.*

### Media móvil 7d – Errores comunes

| Error | Solución |
|-------|----------|
| Eje X muestra rangos 350–360, 360–370, etc. | Estás usando `rolling_avg_7d` en X. Cambia a **`date`** en el eje X. |
| Binning activado en X | Desactiva binning. El eje X debe ser `date` con cada día como punto. |
| Eje Y como "sum(rolling_avg_7d)" | Puedes usar Label Override → **Duración media 7d (s)** |

---

## Resumen rápido

1. **Charts** → conectar cluster si hace falta.
2. **Data Sources** → Add Data Source → Create Charts View → pegar pipeline JSON → Save.
3. Repetir para las 10 pipelines del listado.
4. **Dashboards** → Create Dashboard.
5. Add Chart → elegir Data Source → configurar ejes → Add Chart.
6. Mover y redimensionar hasta tener el dashboard completo.

---

## Nota sobre el formato de las pipelines

En el editor de Charts View, las pipelines se escriben como **array JSON**. Si copias desde `aggregation_pipelines.js`, asegúrate de:

- Usar comillas dobles `"` en las claves.
- Sustituir `null` por `null` (JavaScript) que en JSON sigue siendo `null`.
- Eliminar puntos y comas y comentarios.

Charts acepta el formato de agregación estándar de MongoDB.
