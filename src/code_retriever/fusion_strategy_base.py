from abc import ABC, abstractmethod
from code_retriever.search_base import SearchResult


class FusionStrategyBase(ABC):
    @abstractmethod
    def merge(
        self, outputs: list[list[SearchResult]], no_of_outputs: int
    ) -> list[SearchResult]:
        pass
