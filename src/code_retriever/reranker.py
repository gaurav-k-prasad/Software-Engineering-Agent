from code_retriever.reranker_base import RerankerBase
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from structs import SearchResult


def _extract_scores_from_logits(logits: torch.Tensor) -> list[float]:
    if logits.ndim == 1:
        return logits.float().tolist()

    if logits.ndim == 2 and logits.shape[-1] == 1:
        return logits[:, 0].float().tolist()

    if logits.ndim == 2 and logits.shape[-1] > 1:
        probs = torch.softmax(logits, dim=-1)
        return probs[:, -1].float().tolist()

    return logits.view(-1).float().tolist()


class Reranker(RerankerBase):
    def __init__(
        self,
        tokenizer_name: str = "BAAI/bge-reranker-base",
        model_name: str = "BAAI/bge-reranker-base",
        device="cpu",
    ) -> None:
        self.tokenizer_name = tokenizer_name
        self.model_name = model_name
        self.device = device

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(
            device
        )
        self.model.eval()

    def rerank(
        self, query: str, texts: list[str], chunk_ids: list[str], no_of_outputs: int
    ) -> list[SearchResult]:
        if len(texts) != len(chunk_ids):
            raise ValueError("Length of texts and chunk_ids should be same.")

        pairs = [[query, text] for text in texts]
        with torch.no_grad():
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512,
            ).to(self.device)
            logits = self.model(**inputs, return_dict=True).logits
            scores = _extract_scores_from_logits(logits)

            indices = list(sorted(enumerate(scores), key=lambda x: -x[1]))

        return [
            SearchResult(chunk_ids[idx], relevance)
            for idx, relevance in indices[:no_of_outputs]
        ]


if __name__ == "__main__":
    rr = Reranker()
    query = "What is not a panda"
    texts = [
        "Panda is a white creature found in china",
        "Hello world",
        "I am a programming language",
    ]
    chunk_ids = [str(i) for i in range(len(texts))]

    print(rr.rerank(query, texts, chunk_ids, 5))
