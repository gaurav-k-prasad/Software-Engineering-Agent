from collections import defaultdict
import math
from typing import overload
from embedding.tokenizer import Tokenizer
from structs.chunk_meta_data import ChunkMetaData


class BM25_Plus:
    def __init__(
        self,
        k: float = 1.3,
        b: float = 0.5,
        delta: float = 1,
    ) -> None:
        self.inverted_idx: dict[str, dict[int, int]] = defaultdict(dict)
        self.n = 0
        self.docs_len: dict[int, int] = {}
        self.tokdocs_tokidf: dict[str, float] = {}
        self.doc_len_sum = 0
        self.tokenizer = Tokenizer()
        self.k = k
        self.delta = delta
        self.b = b
        self.avg_len = 0
        self.metadatas = []

        self.finalized = (
            False  # Flag to make sure after insertion finalize function is called
        )

    def fit(self, text: str, chunk_idx: int, metadata: ChunkMetaData) -> None:
        tokens = self.tokenizer.tokenize(text)
        doc_len = sum(tokens.values())
        self.metadatas.append(metadata)

        for token, count in tokens.items():
            self.inverted_idx[token][chunk_idx] = count
        self.doc_len_sum += doc_len
        self.docs_len[chunk_idx] = doc_len
        self.n += 1
        self.finalized = False

    def calculate_idf(self, count: int) -> float:
        idf = math.log(((self.n - count + 0.5) / (count + 0.5)) + 1)
        return idf

    def fit_finalize(
        self,
        texts: list[str] | str,
        chunk_idx: list[int] | int,
        metadata: list[ChunkMetaData] | ChunkMetaData,
    ) -> None:
        if (
            isinstance(texts, str)
            and isinstance(chunk_idx, int)
            and isinstance(metadata, ChunkMetaData)
        ):
            texts = [texts]
            chunk_idx = [chunk_idx]
            metadata = [metadata]

        if not (
            isinstance(texts, list)
            and isinstance(chunk_idx, list)
            and isinstance(metadata, list)
        ):
            raise ValueError(
                "Texts, chunk_idx, metdata should be either all multiple or all single"
            )

        if not (len(texts) == len(chunk_idx) == len(metadata)):
            raise ValueError(
                "Length of texts and chunk idx and metadatas should be same"
            )

        for text, curr_chunk_idx, curr_metadata in zip(texts, chunk_idx, metadata):
            self.fit(text, curr_chunk_idx, curr_metadata)

        self.finalize()

    def finalize(self) -> None:
        if self.n == 0:
            raise ValueError("Cannot finalize empty corpus")

        for token, docs in self.inverted_idx.items():
            count = len(docs)
            self.tokdocs_tokidf[token] = self.calculate_idf(count)
        self.avg_len = self.doc_len_sum / self.n
        self.finalized = True

    def average_length(self) -> float:
        if self.n == 0:
            raise ValueError("No data in corpus")

        return self.doc_len_sum / self.n

    def _search(self, query: str, n_results: int = -1) -> list[tuple[int, float]]:
        if not self.finalized:
            raise ValueError("BM25+ not finalized. Call obj.finalize() then search")

        tokens = self.tokenizer.tokenize(query)
        avg_len = self.avg_len
        res: list[tuple[int, float]] = []

        docs: dict[int, int] = {}
        for token in tokens:
            token_docs = self.inverted_idx[token]
            docs.update(
                {token_doc: self.docs_len[token_doc] for token_doc in token_docs.keys()}
            )

        for doc_id, doc_len in docs.items():
            bm25 = 0
            # if doc_id == 82:
                # print(doc_id, doc_len, self.metadatas[doc_id])
            for token in tokens:
                f_qi_D = self.inverted_idx[token].get(doc_id, 0)
                if f_qi_D == 0:
                    continue

                idf = self.tokdocs_tokidf[token]

                tf = (f_qi_D * (self.k + 1)) / (
                    f_qi_D + self.k * (1 - self.b + self.b * (doc_len / avg_len))
                )
                tf += self.delta  # using bm+

                bm25 += tf * idf
            #     if doc_id == 82:
            #         print(token, tf, idf, tf * idf)
            
            # if doc_id == 82:
            #     print(bm25)
            res.append((doc_id, bm25))

        res.sort(key=lambda x: -x[1])
        if n_results == -1:
            return res
        return res[:n_results]

    @overload
    def search(self, query: str, no_of_outputs: int) -> list[ChunkMetaData]: ...

    @overload
    def search(
        self, query: list[str], no_of_outputs: int
    ) -> list[list[ChunkMetaData]]: ...

    def search(
        self, query: str | list[str], no_of_outputs: int = -1
    ) -> list[ChunkMetaData] | list[list[ChunkMetaData]]:
        is_single_query = False
        if isinstance(query, str):
            is_single_query = True
            query = [query]

        res: list[list[ChunkMetaData]] = []
        for q in query:
            curr: list[ChunkMetaData] = []
            id_bm = self._search(q, no_of_outputs)
            for i, (_id, _) in enumerate(id_bm):
                # print(i, _id, _)
                curr.append(self.metadatas[_id])
            res.append(curr)

        if is_single_query:
            return res[0]
        return res
