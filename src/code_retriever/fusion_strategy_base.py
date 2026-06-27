from abc import ABC, abstractmethod
from .search_code_base import SearchResult


class FusionStrategyBase(ABC):
    @abstractmethod
    def merge(
        self, outputs: list[list[SearchResult]], no_of_outputs: int
    ) -> list[SearchResult]:
        pass
