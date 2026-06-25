from typing import overload

from tqdm import tqdm
from transformers import AutoModel
import faiss
import torch
from structs.chunk_meta_data import ChunkMetaData
from utils.constants import BATCH_SIZE, DIMENSIONS, CODE_MAX_LENGTH
from utils.embed_input import datadict2embed_input


class FAISS:
    def __init__(
        self,
        model_name: str = "jinaai/jina-embeddings-v2-base-code",
        batch_size=BATCH_SIZE,
    ) -> None:
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.index = faiss.IndexHNSWFlat(DIMENSIONS, 32, faiss.METRIC_L2)
        self.metadatas = []
        self.batch_size = batch_size

    def embed_and_store(
        self,
        texts: list[str],
        metadatas: list[ChunkMetaData],
    ) -> None:
        self.metadatas.extend(metadatas)
        batch: list[str] = []
        batches: list[list[str]] = []

        for i, text in enumerate(texts):
            batch.append(text)

            if len(batch) == BATCH_SIZE or i == len(texts) - 1:
                batches.append(batch)
                batch = []

        print("Embedding and saving batches: ")
        for batch in tqdm(batches):
            embeddings = self.model.encode(
                batch,
                max_length=CODE_MAX_LENGTH,
            )

            self.index.add(embeddings)

    @overload
    def search(self, query: str, no_of_outputs: int) -> list[ChunkMetaData]: ...

    @overload
    def search(
        self, query: list[str], no_of_outputs: int
    ) -> list[list[ChunkMetaData]]: ...

    def search(
        self, query: str | list[str], no_of_outputs: int
    ) -> list[ChunkMetaData] | list[list[ChunkMetaData]]:
        is_single_query = False
        if isinstance(query, str):
            is_single_query = True
            query = [query]

        res: list[list[ChunkMetaData]] = []

        indices_n_query = self._search_indices(query, no_of_outputs)
        for indices in indices_n_query:
            curr: list[ChunkMetaData] = []
            for index in indices:
                curr.append(self.metadatas[index])

            res.append(curr)

        if is_single_query:
            return res[0]
        return res

    def _search_indices(self, query: list[str], no_of_outputs: int) -> list[list[int]]:
        query_vector = self.model.encode(
            query,
            max_length=CODE_MAX_LENGTH,
        )

        distances, indices = self.index.search(query_vector, k=no_of_outputs)

        return indices.tolist()
