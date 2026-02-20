import logging
from collections.abc import Iterator
from pathlib import Path

from src.config import Settings
from src.constants import COLLECTION_INDEXES
from src.repository import MongoPipelineEventsRepository
from src.ingest.reader import CsvReader
from src.ingest.transformer import transform_row
from src.ingest.writer import BulkWriter

logger = logging.getLogger(__name__)


def _documents_stream(csv_path: str | Path) -> Iterator[dict]:
    reader = CsvReader(csv_path)
    for row in reader.read_rows():
        yield transform_row(row)


class IngestOrchestrator:
    def __init__(self, settings: Settings) -> None:
        settings.validate()
        self._settings = settings
        self._repo = MongoPipelineEventsRepository(
            settings.mongodb_uri,
            settings.database,
            settings.collection,
        )

    def run(self, csv_path: str | None = None, drop_existing: bool = False) -> int:
        path = csv_path or self._settings.default_csv_path
        if drop_existing:
            self._repo.drop_collection()
            logger.info("Colección %s.%s eliminada", self._settings.database, self._settings.collection)

        docs = _documents_stream(path)
        writer = BulkWriter(self._repo, self._settings.batch_size)
        total = writer.write(docs)

        self._repo.ensure_indexes(COLLECTION_INDEXES)
        logger.info("Índices creados en %s", self._settings.collection)
        self._repo.close()
        return total
