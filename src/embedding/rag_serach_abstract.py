from abc import ABC, abstractmethod
from typing import overload

from structs.chunk_meta_data import ChunkMetaData


class SearchCodeBase(ABC):
    @abstractmethod
    @overload
    def search(self, query: str, no_of_outputs: int) -> list[ChunkMetaData]:
        """Search for a single query"""
        pass

    @abstractmethod
    @overload
    def search(self, query: list[str], no_of_outputs: int) -> list[list[ChunkMetaData]]:
        """Search for a multiple queries"""
        pass
