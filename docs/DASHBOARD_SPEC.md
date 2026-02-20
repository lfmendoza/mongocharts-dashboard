# Especificación del Dashboard: CD Pipeline Analytics

El dashboard se construye usando **Charts Views** basadas en las 6 aggregation pipelines. Cada chart toma su data de una pipeline concreta.

---

## Data sources: pipelines por chart

| Chart/KPI | Pipeline | Campo(s) para el chart |
|-----------|----------|------------------------|
| Deployments por Semana | view_deployments_by_week | X: _id, Y: count |
| CFR por Región | view_cfr_by_region | X: region, Y: cfr_pct |
| Top Failure Reasons | view_top_failure_reasons | X: _id, Y: count |
| SLA por Equipo | view_sla_by_team | X: team, Y: sla_pct |
| Distribución por Trigger | view_trigger_distribution | X: _id, Y: count |
| Duración media móvil 7d | 2 ($setWindowFields) | X: date, Y: rolling_avg_7d |
| Percentiles por Equipo | 3 | X: team, Y: p50/p90/p99 |
| Histograma duración | 4 ($bucket) | X: range, Y: count, serie: failure_rate_pct |
| Eficiencia por Autor | 5 | X: author, Y: efficiency_score |
| Fallos por Environment | 6 | environment + top_reasons |

---

## Pipeline 1 ($facet) – 5 charts

En `aggregation_pipelines.js` hay variantes ya preparadas para Charts: `view_deployments_by_week`, `view_cfr_by_region`, `view_top_failure_reasons`, `view_sla_by_team`, `view_trigger_distribution`.

| Charts View | Constante en .js | Chart | X / Categoría | Y / Valor |
|-------------|------------------|-------|---------------|-----------|
| Deployments por Semana | view_deployments_by_week | Line/Area | _id | count |
| CFR por Región | view_cfr_by_region | Bar | region | cfr_pct |
| Top Failure Reasons | view_top_failure_reasons | Bar | _id | count |
| SLA por Equipo | view_sla_by_team | Bar horizontal | team | sla_pct |
| Distribución Trigger | view_trigger_distribution | Donut | _id | count |

---

## Pipeline 2 – Media móvil 7 días

**Charts View:** Crear data source con `pipeline_2_rolling_avg_duration` (ver `aggregation_pipelines.js`).

**Chart:** Line
- X: `date`
- Y: `rolling_avg_7d` (o `avg_duration`)
- Título: "Duración promedio – media móvil 7d"

---

## Pipeline 3 – Percentiles por equipo

**Charts View:** Data source = `pipeline_3_percentiles_by_team`.

**Chart:** Bar horizontal
- Y: `team`
- X: `p50_seconds`, `p90_seconds`, `p99_seconds` (3 series)
- Título: "Percentiles de duración por equipo"

---

## Pipeline 4 – Histograma de duración

**Charts View:** Data source = `pipeline_4_duration_histogram_with_failures`.

**Chart:** Bar
- X: `range`
- Y: `count` (o `failure_rate_pct`)
- Título: "Histograma de duración (seg)"

---

## Pipeline 5 – Eficiencia por autor

**Charts View:** Data source = `pipeline_5_author_efficiency_score`.

**Chart:** Bar horizontal
- Y: `author`
- X: `efficiency_score`
- Título: "Eficiencia por autor"

---

## Pipeline 6 – Correlación de fallos

**Charts View:** Data source = `pipeline_6_failure_correlation_analysis`.

**Chart:** Table o estructura anidada
- Columnas: `environment`, `top_reasons` (array de {reason, count, avg_retry, avg_duration})
- Título: "Fallos por environment y causa"

---

## KPIs (colección directa o pipeline 1)

| KPI | Origen | Config |
|-----|--------|--------|
| Deployments exitosos 30d | pipeline_events + filtros event_type=deployment, status=success, timestamp 30d | Number Chart |
| CFR 30d | pipeline_1 cfr_by_region agregado o pipeline_events | Gauge, Min 0 Max 100 Target 15 |

---

## Creación en MongoDB Charts

1. Atlas → Charts → Conectar cluster
2. Data Sources → Add Data Source → Create Charts View (aggregation)
3. Copiar cada pipeline desde `scripts/aggregation_pipelines.js`:
   - view_deployments_by_week, view_cfr_by_region, view_top_failure_reasons, view_sla_by_team, view_trigger_distribution
   - pipeline_2_rolling_avg_duration
   - pipeline_3_percentiles_by_team
   - pipeline_4_duration_histogram_with_failures
   - pipeline_5_author_efficiency_score
   - pipeline_6_failure_correlation_analysis
4. Crear dashboard → Add Chart para cada view según la tabla de mapeo
