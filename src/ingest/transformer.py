import logging
from datetime import datetime

from src.constants import FLOAT_FIELDS, INT_FIELDS

logger = logging.getLogger(__name__)


def transform_row(row: dict) -> dict:
    doc = dict(row)
    if "timestamp" in doc and doc["timestamp"]:
        try:
            doc["timestamp"] = datetime.fromisoformat(doc["timestamp"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            logger.warning("Timestamp inválido en fila: %s", doc.get("event_id", "?"))

    for field in INT_FIELDS:
        if field in doc and doc.get(field) != "":
            try:
                doc[field] = int(float(doc[field]))
            except (ValueError, TypeError):
                doc[field] = 0

    for field in FLOAT_FIELDS:
        if field in doc and doc.get(field) != "":
            try:
                doc[field] = float(doc[field])
            except (ValueError, TypeError):
                doc[field] = 0.0

    return doc
