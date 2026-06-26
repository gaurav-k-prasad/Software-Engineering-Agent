from collections import defaultdict
from typing import overload

from embedding.document_store import DocumentStore
from embedding.fusion_strategy_abstract import FusionStrategy
from structs.chunk_meta_data import ChunkMetaData
from utils.constants import BATCH_SIZE
from .faiss import FAISS
from embedding.bm25 import BM25_Plus
from embedding.rag_serach_abstract import SearchCodeBase, SearchResult


class HybridSearch(SearchCodeBase):
    def __init__(
        self,
        backends: list[SearchCodeBase],
        fusion_strategy: FusionStrategy,
    ) -> None:
        if len(backends) == 0:
            raise ValueError("atleast one backend index required")

        self.backends = backends
        self.fusion_strategy = fusion_strategy

    def fit(self, texts: str | list[str], chunk_ids: str | list[str]) -> None:
        for backend in self.backends:
            backend.fit(texts, chunk_ids)

    @overload
    def search(self, query: str, no_of_outputs: int) -> list[SearchResult]:
        """Search for a single query"""
        pass

    @overload
    def search(self, query: list[str], no_of_outputs: int) -> list[list[SearchResult]]:
        """Search for a multiple queries"""
        pass

    def search(
        self, query: str | list[str], no_of_outputs: int
    ) -> list[SearchResult] | list[list[SearchResult]]:
        is_single_query = False
        if isinstance(query, str):
            is_single_query = True
            query = [query]

        outputs: list[list[list[SearchResult]]] = [
            backend.search(query, no_of_outputs) for backend in self.backends
        ]

        res: list[list[SearchResult]] = []
        n_queries = len(query)

        for i in range(n_queries):
            output = [output[i] for output in outputs]
            res.append(self.fusion_strategy.merge(output, no_of_outputs))

        if is_single_query:
            return res[0]
        return res
