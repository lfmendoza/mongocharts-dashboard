import csv
import logging
from pathlib import Path

from src.constants import REQUIRED_CSV_FIELDS
from src.exceptions import IngestError

logger = logging.getLogger(__name__)


class CsvReader:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        if not self._path.exists():
            raise IngestError(f"CSV no encontrado: {path}")
        self._fieldnames: list[str] | None = None

    def _validate_header(self, fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise IngestError("CSV vacío o sin encabezados")
        for required in REQUIRED_CSV_FIELDS:
            if required not in fieldnames:
                raise IngestError(f"CSV debe contener columna '{required}'")

    def read_rows(self):
        with open(self._path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self._fieldnames = reader.fieldnames
            self._validate_header(self._fieldnames)
            for row in reader:
                yield row
