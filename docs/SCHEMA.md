# Esquema de Datos: pipeline_events

## Colección

**Base de datos:** `platform_analytics`  
**Colección:** `pipeline_events`

## Documento de ejemplo

```json
{
  "_id": ObjectId("..."),
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": ISODate("2024-12-15T14:32:00.000Z"),
  "event_type": "deployment",
  "status": "success",
  "environment": "staging",
  "application": "api-gateway",
  "region": "us-east-1",
  "team": "platform",
  "duration_seconds": 120,
  "build_number": 42,
  "branch": "main",
  "trigger": "webhook",
  "retry_count": 0,
  "tests_run": 0,
  "tests_passed": 0,
  "cpu_seconds": 140,
  "artifact_size_mb": 0,
  "author": "maria.garcia",
  "sla_met": 1,
  "failure_reason": ""
}
```

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `_id` | ObjectId | ID del documento |
| `event_id` | string | UUID único del evento |
| `timestamp` | Date | Momento de ejecución |
| `event_type` | string | deployment, build, pipeline |
| `status` | string | success, failed, cancelled |
| `environment` | string | dev, staging, production |
| `application` | string | Microservicio |
| `region` | string | Región/datacenter |
| `team` | string | Equipo responsable |
| `duration_seconds` | int | Duración en segundos |
| `build_number` | int | Número de build |
| `branch` | string | Rama Git |
| `trigger` | string | webhook, merge_request, manual, schedule |
| `retry_count` | int | Reintentos (0–3) |
| `tests_run` | int | Tests ejecutados (build/pipeline) |
| `tests_passed` | int | Tests pasados |
| `cpu_seconds` | int | Tiempo CPU (proxy de coste) |
| `artifact_size_mb` | float | Tamaño de artefactos en MB |
| `author` | string | Autor del commit/deploy |
| `sla_met` | int | 1 si cumplió SLA, 0 si no |
| `failure_reason` | string | timeout, test_failure, infra_error, etc. (si falló) |

## Índices

```javascript
db.pipeline_events.createIndex({ "timestamp": 1 })
db.pipeline_events.createIndex({ "environment": 1, "timestamp": 1 })
db.pipeline_events.createIndex({ "event_type": 1, "status": 1 })
db.pipeline_events.createIndex({ "team": 1 })
db.pipeline_events.createIndex({ "region": 1 })
db.pipeline_events.createIndex({ "branch": 1 })
db.pipeline_events.createIndex({ "trigger": 1 })
db.pipeline_events.createIndex({ "author": 1 })
db.pipeline_events.createIndex({ "failure_reason": 1 })
```
