from typing import overload
from transformers import AutoModel
import faiss
from code_retriever.search_base import SearchBase, SearchResult
from utils.constants import BATCH_SIZE, DIMENSIONS, CODE_MAX_LENGTH


class FAISS(SearchBase):
    def __init__(
        self,
        model_name: str = "jinaai/jina-embeddings-v2-base-code",
        batch_size=BATCH_SIZE,
        device="cpu",
    ) -> None:
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(
            device
        )

        self.index = faiss.IndexHNSWFlat(DIMENSIONS, 32, faiss.METRIC_L2)
        self.idx_to_id: dict[int, str] = {}
        self.batch_size = batch_size
        self.curr_idx = 0

    def fit(
        self,
        texts: list[str] | str,
        chunk_ids: list[str] | str,
    ) -> None:
        if isinstance(texts, str) and isinstance(chunk_ids, str):
            texts = [texts]
            metadatas = [chunk_ids]

        if not (isinstance(texts, list) and isinstance(chunk_ids, list)):
            raise ValueError(
                "texts and metadatas should be either both singular or both list"
            )

        if not (len(texts) == len(chunk_ids)):
            raise ValueError(
                "Length of texts and chunk idx and metadatas should be same"
            )

        batch: list[str] = []
        batches: list[list[str]] = []

        for i, (chunk_id, text) in enumerate(zip(chunk_ids, texts)):
            batch.append(text)
            self.idx_to_id[self.curr_idx] = chunk_id
            self.curr_idx += 1

            if len(batch) == self.batch_size or i == len(texts) - 1:
                batches.append(batch)
                batch = []
        for batch in batches:
            embeddings = self.model.encode(
                batch,
                max_length=CODE_MAX_LENGTH,
            )

            self.index.add(embeddings)

    def _search(self, query: str, no_of_outputs: int) -> list[tuple[str, float]]:
        query_vector = self.model.encode(
            [query],
            max_length=CODE_MAX_LENGTH,
        )
        distances, indices = self.index.search(query_vector, k=no_of_outputs)
        distances, indices = distances[0].tolist(), indices[0].tolist()
        res: list[tuple[str, float]] = []

        for idx, dist in zip(indices, distances):
            if idx == -1:
                continue
            item = (self.idx_to_id[idx], dist)
            res.append(item)
        return res

    @overload
    def search(self, query: str, no_of_outputs: int) -> list[SearchResult]: ...

    @overload
    def search(
        self, query: list[str], no_of_outputs: int
    ) -> list[list[SearchResult]]: ...

    def search(
        self, query: str | list[str], no_of_outputs: int
    ) -> list[SearchResult] | list[list[SearchResult]]:
        is_single_query = False
        if isinstance(query, str):
            is_single_query = True
            query = [query]

        res: list[list[SearchResult]] = []

        for q in query:
            curr: list[SearchResult] = []
            id_dist = self._search(q, no_of_outputs)
            for _id, dist in id_dist:
                curr.append(SearchResult(_id, dist))
            res.append(curr)

        if is_single_query:
            return res[0]
        return res
