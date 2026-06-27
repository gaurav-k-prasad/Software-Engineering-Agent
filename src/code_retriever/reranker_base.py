from abc import ABC, abstractmethod
from structs import SearchResult


class RerankerBase(ABC):
    @abstractmethod
    def rerank(
        self, query: str, texts: list[str], chunk_ids: list[str], no_of_outputs: int
    ) -> list[SearchResult]:
        pass
