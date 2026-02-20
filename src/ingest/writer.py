import logging
from collections.abc import Iterator

from src.exceptions import IngestError
from src.repository import PipelineEventsRepository

logger = logging.getLogger(__name__)


class BulkWriter:
    def __init__(self, repository: PipelineEventsRepository, batch_size: int) -> None:
        self._repo = repository
        self._batch_size = batch_size

    def write(self, documents: Iterator[dict]) -> int:
        try:
            return self._repo.bulk_insert(documents, self._batch_size)
        except Exception as e:
            raise IngestError(f"Error en inserción bulk: {e}") from e
