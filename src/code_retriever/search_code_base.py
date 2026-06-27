from abc import ABC, abstractmethod
from typing import overload
from structs import SearchResult


class SearchCodeBase(ABC):
    @abstractmethod
    @overload
    def search(self, query: str, no_of_outputs: int) -> list[SearchResult]:
        """Search for a single query"""
        pass

    @abstractmethod
    @overload
    def search(self, query: list[str], no_of_outputs: int) -> list[list[SearchResult]]:
        """Search for a multiple queries"""
        pass

    @abstractmethod
    def fit(self, texts: list[str] | str, chunk_ids: list[str] | str): ...
