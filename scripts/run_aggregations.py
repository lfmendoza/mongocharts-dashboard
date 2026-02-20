#!/usr/bin/env python3
"""Ejecuta pipelines de agregación contra pipeline_events."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.exceptions import ConfigError
from src.repository import MongoPipelineEventsRepository
from src.pipelines import PIPELINE_REGISTRY


def main() -> None:
    cfg = load_config(PROJECT_ROOT)
    try:
        cfg.validate()
    except ConfigError as e:
        print(str(e))
        sys.exit(1)

    repo = MongoPipelineEventsRepository(cfg.mongodb_uri, cfg.database, cfg.collection)

    for name, fn in PIPELINE_REGISTRY.items():
        print(f"\n--- {name} ---")
        try:
            cursor = repo.aggregate(fn())
            results = list(cursor)
            print(json.dumps(results[:5] if len(results) > 5 else results, indent=2, default=str))
            print(f"... ({len(results)} documentos)")
        except Exception as e:
            print(f"Error: {e}")

    repo.close()


if __name__ == "__main__":
    main()
