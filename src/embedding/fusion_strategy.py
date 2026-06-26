from collections import defaultdict

from embedding.fusion_strategy_abstract import FusionStrategy
from embedding.rag_serach_abstract import SearchResult


class ReciprocalRankFusion(FusionStrategy):
    def merge(
        self, outputs: list[list[SearchResult]], no_of_outputs: int = -1
    ) -> list[SearchResult]:
        scores: defaultdict[str, float] = defaultdict(float)

        for output in outputs:
            for rank, doc in enumerate(output, start=1):
                scores[doc.chunk_id] += 1 / (60 + rank)

        sorted_docs = sorted(scores.items(), key=lambda x: -x[1])

        res: list[SearchResult] = []
        for _id, dist in sorted_docs:
            res.append(SearchResult(_id, dist))

        if no_of_outputs == -1:
            return res
        return res[:no_of_outputs]
