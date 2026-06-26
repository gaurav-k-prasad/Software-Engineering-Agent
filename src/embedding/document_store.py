from typing import overload
from structs.chunk_meta_data import ChunkMetaData


class DocumentStore:
    def __init__(self) -> None:
        self.docs: dict[str, ChunkMetaData] = {}

    @overload
    def insert(self, docs: ChunkMetaData) -> None:
        pass

    @overload
    def insert(self, docs: list[ChunkMetaData]) -> None:
        pass

    def insert(self, docs: ChunkMetaData | list[ChunkMetaData]) -> None:
        if isinstance(docs, ChunkMetaData):
            docs = [docs]

        for doc in docs:
            self.docs[doc.chunk_id] = doc

    @overload
    def get(self, chunk_ids: str) -> ChunkMetaData:
        pass

    @overload
    def get(self, chunk_ids: list[str]) -> list[ChunkMetaData]:
        pass

    def get(self, chunk_ids: str | list[str]) -> ChunkMetaData | list[ChunkMetaData]:
        is_single_query = False
        if isinstance(chunk_ids, str):
            chunk_ids = [chunk_ids]
            is_single_query = True

        res: list[ChunkMetaData] = []

        for chunk_id in chunk_ids:
            if chunk_id not in self.docs:
                raise KeyError("Chunk id not found in document store")

            res.append(self.docs[chunk_id])

        if is_single_query:
            return res[0]
        return res
