# CD Pipeline Analytics

Dashboard de métricas DevOps (deployments, builds, pipelines) con ingesta CSV a MongoDB Atlas y visualización en MongoDB Charts. [https://youtu.be/1S47Xgn2-68]

## Arquitectura

```
generate_data.py → pipeline_events.csv → ingest.py → MongoDB Atlas → MongoDB Charts
```

- **Patrón Repository**: `MongoPipelineEventsRepository` abstrae el acceso a MongoDB.
- **Pipeline de ingesta**: `CsvReader` → `transform_row` → `BulkWriter` (via `IngestOrchestrator`).
- **Registry de pipelines**: pipelines de agregación centralizadas en `src.pipelines`.
- **Config validada**: `Settings` con `load_config()` y validación (ConfigError si URI vacía).

## Requisitos

- Python 3.10+
- Cuenta MongoDB Atlas con cluster (tier gratuito M0 suficiente)
- Credenciales de conexión (URI)

## Instalación

```bash
# Clonar o navegar al proyecto
cd mongocharts-dashboard

# Crear entorno virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar MONGODB_URI con tu conexión a Atlas
```

## Uso

### 1. Generar datos CSV

```bash
python scripts/generate_data.py
```

Genera `data/raw/pipeline_events.csv` con ~100.000 eventos por defecto (semilla 42). Para M0 (512 MB) se recomienda hasta ~1.5M registros.

Opciones:
- `--rows 500000` - Más registros (hasta ~1.5M en M0)
- `--seed 123` - Otra semilla
- `--days 365` - Rango temporal en días

### 2. Ingesta a MongoDB Atlas

```bash
# Primera ejecución (crea colección)
python scripts/ingest.py

# Re-ejecución con limpieza previa
python scripts/ingest.py --drop
```

Requisitos:
- `MONGODB_URI` configurada en `.env`
- CSV existente en `data/raw/pipeline_events.csv`

### 3. Dashboard en MongoDB Charts

**Guía paso a paso:** [docs/GUIA_DASHBOARD.md](docs/GUIA_DASHBOARD.md)

1. En Atlas → Charts → conectar el cluster.
2. Crear Data Sources tipo "Charts View" con las pipelines de [docs/pipelines_for_charts.json](docs/pipelines_for_charts.json).
3. Crear dashboard y añadir gráficos por data source.

### 4. Pipelines de agregación avanzadas

```bash
python scripts/run_aggregations.py
```

Ver [docs/AGGREGATION_PIPELINES.md](docs/AGGREGATION_PIPELINES.md).

## Estructura del proyecto

```
mongocharts-dashboard/
├── data/raw/
│   └── pipeline_events.csv
├── src/
│   ├── config.py             # Settings (load_config, validación)
│   ├── exceptions.py         # ConfigError, IngestError
│   ├── constants.py          # Índices, campos, constantes
│   ├── repository.py         # Repository pattern (MongoDB)
│   ├── ingest/               # Pipeline Reader → Transformer → Writer
│   │   ├── reader.py         # CsvReader
│   │   ├── transformer.py    # transform_row
│   │   ├── writer.py         # BulkWriter
│   │   └── orchestrator.py   # IngestOrchestrator
│   └── pipelines/            # Registry de pipelines de agregación
│       ├── definitions.py
│       └── registry.py
├── scripts/
│   ├── generate_data.py
│   ├── ingest.py
│   ├── run_aggregations.py
│   └── aggregation_pipelines.js
├── docs/
├── .env.example
├── requirements.txt
└── README.md
```

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `MONGODB_URI` | URI de conexión a Atlas | (requerida) |
| `MONGODB_DATABASE` | Base de datos | `platform_analytics` |
| `MONGODB_COLLECTION` | Colección | `pipeline_events` |
| `INGEST_BATCH_SIZE` | Tamaño de lote bulk_write | `1000` |

## Referencias

- [MongoDB Charts](https://www.mongodb.com/docs/charts/)
- [PyMongo Bulk Write](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/bulk-write/)
- [DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)
