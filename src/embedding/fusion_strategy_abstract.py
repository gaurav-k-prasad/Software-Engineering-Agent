from abc import ABC, abstractmethod

from embedding.rag_serach_abstract import SearchResult


class FusionStrategy(ABC):
    @abstractmethod
    def merge(
        self, outputs: list[list[SearchResult]], no_of_outputs: int
    ) -> list[SearchResult]:
        pass
