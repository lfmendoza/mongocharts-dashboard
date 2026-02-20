#!/usr/bin/env python3
"""Ingesta CSV de pipeline_events a Atlas."""

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.exceptions import ConfigError, IngestError
from src.ingest import IngestOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    cfg = load_config(PROJECT_ROOT)
    parser = argparse.ArgumentParser(description="Ingesta CSV de pipeline_events a MongoDB Atlas")
    parser.add_argument(
        "--csv",
        type=str,
        default=cfg.default_csv_path,
        help=f"Ruta al CSV (default: {cfg.default_csv_path})",
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Eliminar colección antes de insertar",
    )
    args = parser.parse_args()
    csv_path = args.csv
    if not Path(csv_path).is_absolute():
        csv_path = str(PROJECT_ROOT / csv_path)

    try:
        orchestrator = IngestOrchestrator(cfg)
        count = orchestrator.run(csv_path=csv_path, drop_existing=args.drop)
        logger.info("Ingesta completada: %d documentos en %s.%s", count, cfg.database, cfg.collection)
    except (ConfigError, IngestError) as e:
        logger.error("%s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
