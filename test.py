import torch

from src.code_retriever.reranker import _extract_scores_from_logits


def test_extract_scores_from_single_logit_per_item() -> None:
    logits = torch.tensor([[2.0], [0.5], [-1.0]])

    scores = _extract_scores_from_logits(logits)

    assert scores == [2.0, 0.5, -1.0]


def test_extract_scores_from_two_class_logits() -> None:
    logits = torch.tensor([[1.0, 2.0], [0.0, 1.0]])

    scores = _extract_scores_from_logits(logits)

    assert scores[0] > scores[1]
    assert len(scores) == 2
