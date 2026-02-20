import os
from dataclasses import dataclass
from pathlib import Path

from src.exceptions import ConfigError


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    database: str
    collection: str
    batch_size: int
    default_csv_path: str

    def validate(self) -> None:
        if not self.mongodb_uri or not self.mongodb_uri.strip():
            raise ConfigError("MONGODB_URI no configurada")


def _load_env(project_root: Path) -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")
    except ImportError:
        pass


def load_config(project_root: Path | None = None) -> Settings:
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent
    _load_env(project_root)

    return Settings(
        mongodb_uri=os.getenv("MONGODB_URI", "").strip(),
        database=os.getenv("MONGODB_DATABASE", "platform_analytics"),
        collection=os.getenv("MONGODB_COLLECTION", "pipeline_events"),
        batch_size=int(os.getenv("INGEST_BATCH_SIZE", "1000")),
        default_csv_path=os.getenv("CSV_PATH", "data/raw/pipeline_events.csv"),
    )
