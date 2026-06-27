from collections import defaultdict
import math
from typing import overload
from code_retriever.search_base import SearchBase, SearchResult
from code_retriever.tokenizer import Tokenizer


class BM25_Plus(SearchBase):
    def __init__(
        self,
        k: float = 1.3,
        b: float = 0.5,
        delta: float = 1,
    ) -> None:
        self.inverted_idx: dict[str, dict[str, int]] = defaultdict(dict)
        self.n = 0
        self.docs_len: dict[str, int] = {}
        self.tokdocs_tokidf: dict[str, float] = {}
        self.doc_len_sum = 0
        self.tokenizer = Tokenizer()
        self.k = k
        self.delta = delta
        self.b = b
        self.avg_len = 0

        self.finalized = (
            False  # Flag to make sure after insertion finalize function is called
        )

    def fit(self, texts: str | list[str], chunk_ids: str | list[str]) -> None:
        if isinstance(texts, str) and isinstance(chunk_ids, str):
            texts = [texts]
            chunk_ids = [chunk_ids]

        if not (isinstance(texts, list) and isinstance(chunk_ids, list)):
            raise ValueError(
                "texts and chunk_ids should be either both singular or both list"
            )

        if not (len(texts) == len(chunk_ids)):
            raise ValueError("Length of texts and chunk idx should be same")

        self.n += len(texts)
        updated_tokens: set[str] = set()

        for chunk_id, text in zip(chunk_ids, texts):
            tokens = self.tokenizer.tokenize(text)
            doc_len = sum(tokens.values())

            for token, count in tokens.items():
                self.inverted_idx[token][chunk_id] = count
                updated_tokens.add(token)
            self.doc_len_sum += doc_len
            self.docs_len[chunk_id] = doc_len

        self._finalize(updated_tokens)

    def calculate_idf(self, count: int) -> float:
        idf = math.log(((self.n - count + 0.5) / (count + 0.5)) + 1)
        return idf

    def _finalize(self, updated_tokens: set[str]) -> None:
        if self.n == 0:
            raise ValueError("Cannot finalize empty corpus")

        for token in updated_tokens:
            count = len(self.inverted_idx[token])
            self.tokdocs_tokidf[token] = self.calculate_idf(count)
        self.avg_len: float = self.doc_len_sum / self.n
        self.finalized = True

    def average_length(self) -> float:
        if self.n == 0:
            raise ValueError("No data in corpus")

        return self.doc_len_sum / self.n

    def _search(self, query: str, n_results: int = -1) -> list[tuple[str, float]]:
        if not self.finalized:
            raise ValueError("BM25+ not finalized. Call obj.finalize() then search")

        tokens = self.tokenizer.tokenize(query)
        avg_len = self.avg_len
        res: list[tuple[str, float]] = []

        docs: dict[str, int] = {}
        for token in tokens:
            token_docs = self.inverted_idx[token]
            docs.update(
                {token_doc: self.docs_len[token_doc] for token_doc in token_docs.keys()}
            )

        for doc_id, doc_len in docs.items():
            bm25 = 0
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
            res.append((doc_id, bm25))

        res.sort(key=lambda x: -x[1])
        if n_results == -1:
            return res
        return res[:n_results]

    @overload
    def search(self, query: str, no_of_outputs: int) -> list[SearchResult]: ...

    @overload
    def search(
        self, query: list[str], no_of_outputs: int
    ) -> list[list[SearchResult]]: ...

    def search(
        self, query: str | list[str], no_of_outputs: int = -1
    ) -> list[SearchResult] | list[list[SearchResult]]:
        is_single_query = False
        if isinstance(query, str):
            is_single_query = True
            query = [query]

        res: list[list[SearchResult]] = []
        for q in query:
            curr: list[SearchResult] = []
            id_bm = self._search(q, no_of_outputs)
            for _id, dist in id_bm:
                curr.append(SearchResult(_id, dist))
            res.append(curr)

        if is_single_query:
            return res[0]
        return res
