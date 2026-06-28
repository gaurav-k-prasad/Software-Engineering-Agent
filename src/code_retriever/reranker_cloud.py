from code_retriever.reranker_base import RerankerBase
import cohere
from dotenv import load_dotenv
import os

from structs import SearchResult

load_dotenv()


class RerankerCloud(RerankerBase):
    def __init__(self, api_key: str | None = None, model: str = "rerank-v3.5") -> None:
        api_key = api_key or os.environ.get("COHERE_API_KEY")
        self.co = cohere.ClientV2(api_key)
        self.model = model

    def rerank(
        self, query: str, texts: list[str], chunk_ids: list[str], no_of_outputs: int
    ) -> list[SearchResult]:
        response = self.co.rerank(
            model=self.model,
            query=query,
            documents=texts,
            top_n=no_of_outputs,
        )

        res: list[SearchResult] = [
            SearchResult(chunk_ids[resp.index], resp.relevance_score)
            for resp in response.results
        ]

        return res
