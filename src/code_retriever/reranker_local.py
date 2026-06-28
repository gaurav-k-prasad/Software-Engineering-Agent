from code_retriever.reranker_base import RerankerBase
import torch
from transformers.models.auto.modeling_auto import AutoModel
from structs import SearchResult


class RerankerLocal(RerankerBase):
    def __init__(
        self,
        model_name: str = "jinaai/jina-reranker-v3",
        device="cpu",
    ) -> None:
        self.model_name = model_name
        self.device = device

        self.model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
        ).to(device)
        self.model.eval()

    def rerank(
        self, query: str, texts: list[str], chunk_ids: list[str], no_of_outputs: int
    ) -> list[SearchResult]:
        if len(texts) != len(chunk_ids):
            raise ValueError("Length of texts and chunk_ids should be same.")
        with torch.inference_mode():
            results = self.model.rerank(query, texts, top_n=no_of_outputs)
            indices = list(sorted(results, key=lambda x: -x["relevance_score"]))
        return [
            SearchResult(chunk_ids[int(data["index"])], float(data["relevance_score"]))
            for data in indices
        ]


if __name__ == "__main__":
    rr = RerankerLocal()
    query = "What is not a panda"
    texts = [
        "Panda is a white creature found in china",
        "Hello world",
        "I am a programming language",
    ]
    chunk_ids = [str(i) for i in range(len(texts))]

    print(rr.rerank(query, texts, chunk_ids, 5))
