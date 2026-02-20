from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database


class PipelineEventsRepository(ABC):
    @abstractmethod
    def bulk_insert(self, documents: Iterator[dict[str, Any]], batch_size: int) -> int:
        pass

    @abstractmethod
    def drop_collection(self) -> None:
        pass

    @abstractmethod
    def ensure_indexes(self, index_specs: list[Any]) -> None:
        pass

    @abstractmethod
    def aggregate(self, pipeline: list[dict[str, Any]]) -> Cursor:
        pass

    @abstractmethod
    def count_documents(self) -> int:
        pass


class MongoPipelineEventsRepository(PipelineEventsRepository):
    def __init__(self, uri: str, database: str, collection: str) -> None:
        self._client = MongoClient(uri)
        self._db: Database = self._client[database]
        self._coll: Collection = self._db[collection]

    @property
    def collection(self) -> Collection:
        return self._coll

    def bulk_insert(self, documents: Iterator[dict[str, Any]], batch_size: int) -> int:
        from pymongo.operations import InsertOne

        total = 0
        batch: list[InsertOne] = []
        for doc in documents:
            batch.append(InsertOne(doc))
            if len(batch) >= batch_size:
                result = self._coll.bulk_write(batch, ordered=False)
                total += result.inserted_count
                batch = []
        if batch:
            result = self._coll.bulk_write(batch, ordered=False)
            total += result.inserted_count
        return total

    def drop_collection(self) -> None:
        self._coll.drop()

    def ensure_indexes(self, index_specs: list[Any]) -> None:
        for spec in index_specs:
            if isinstance(spec, str):
                self._coll.create_index(spec)
            else:
                self._coll.create_index(spec)

    def aggregate(self, pipeline: list[dict[str, Any]]) -> Cursor:
        return self._coll.aggregate(pipeline, allowDiskUse=True)

    def count_documents(self) -> int:
        return self._coll.count_documents({})

    def close(self) -> None:
        self._client.close()
