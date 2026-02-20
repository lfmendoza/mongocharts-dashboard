# Aggregation Pipelines

## 1. $facet – Dashboard multi-dimensional

Una consulta devuelve: deployments por semana, CFR por región, top failure reasons, SLA por equipo, distribución por trigger.

## 2. $setWindowFields – Media móvil 7 días

Serie temporal suavizada de duración diaria de pipelines. Requiere MongoDB 5.0+.

## 3. Percentiles P50/P90/P99 por equipo

SLOs de latencia. Salida: `p50_seconds`, `p90_seconds`, `p99_seconds` por team.

## 4. $bucket – Histograma de duración

Rangos 0–60s, 60–120s, … hasta overflow. Incluye `failure_rate_pct` por bucket.

## 5. Score de eficiencia por autor

Métrica compuesta: throughput + success + SLA + coste CPU. Salida: `efficiency_score` por autor.

## 6. Correlación de fallos

Top 5 causas por environment con count, avg_retry, avg_duration, trigger.

---

## Ejecución

mongosh:
```javascript
use platform_analytics;
db.pipeline_events.aggregate(pipeline_1_facet_dashboard, { allowDiskUse: true });
```

Python:
```bash
python scripts/run_aggregations.py
```
