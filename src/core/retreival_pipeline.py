from chunker import PythonChunker
from code_retriever import (
    ChunkStore,
    SearchBase,
    RerankerBase,
)
from tqdm import tqdm
from structs.chunk_meta_data import ChunkMetaData


class RetrievalPipeline:
    def __init__(
        self,
        search_strategy: SearchBase,
        reranker: RerankerBase | None,
        chunk_store: ChunkStore,
        chunker: PythonChunker,
    ) -> None:
        self.search_strategy: SearchBase = search_strategy
        self.reranker: RerankerBase | None = reranker
        self.chunk_store: ChunkStore = chunk_store
        self.chunker: PythonChunker = chunker

    def index_repository(self, dir_path: str, save_path: str) -> None:
        with open(save_path, "w") as f:
            for chunks in tqdm(self.chunker.chunk_files(dir_path)):
                search_texts: list[str] = []
                chunk_ids: list[str] = []

                for chunk in chunks:
                    search_texts.append(self.chunk_store.metadata_to_search_text(chunk))
                    chunk_ids.append(chunk.chunk_id)

                self.search_strategy.fit(search_texts, chunk_ids)
                self.chunk_store.insert(chunks)
                self.chunk_store.chunks_to_jsonl(chunks, f)

    def search(self, query: str, no_of_outputs: int) -> list[ChunkMetaData]:
        # get thrice the search results from basic search
        search_results = self.search_strategy.search(query, no_of_outputs * 3)

        if self.reranker:
            search_texts: list[str] = []
            chunk_ids: list[str] = []

            for metadata in self.chunk_store.get_from_search_result(search_results):
                search_texts.append(self.chunk_store.metadata_to_search_text(metadata))
                chunk_ids.append(metadata.chunk_id)

            search_results = self.reranker.rerank(
                query,
                search_texts,
                chunk_ids,
                no_of_outputs,
            )
        return self.chunk_store.get_from_search_result(search_results)[:no_of_outputs]
