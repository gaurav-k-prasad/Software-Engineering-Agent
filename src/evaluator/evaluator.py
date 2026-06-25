from typing import Callable, TypedDict
from structs.chunk_meta_data import ChunkMetaData


class SearchQueryData(TypedDict):
    query: str
    expected: list[str]


class Evaluator:
    def evaluate(
        self,
        k: int,
        query_fn: Callable[[str, int], list[ChunkMetaData]],
        target: list[SearchQueryData],
    ) -> dict[str, float]:
        if k <= 0:
            raise ValueError("k should be greater than 0")
        if not target:
            return {"precision": 0, "recall": 0, "mrr": 0}

        avg_precision = 0
        avg_recall = 0
        mrr = 0
        for t in target:
            q = t["query"]
            expected = set(t["expected"])

            if len(expected) == 0:
                continue
            metadatas = query_fn(q, k)
            metadatas_qualified_names = {md.qualified_name for md in metadatas}

            precision = (
                sum((1 for md in metadatas if md.qualified_name in expected)) / k
            )

            recall = sum((1 for e in expected if e in metadatas_qualified_names)) / len(
                expected
            )

            rr = 0.0
            for rank, md in enumerate(metadatas, start=1):
                if md.qualified_name in expected:
                    rr = 1 / rank
                    break

            avg_precision += precision
            avg_recall += recall
            mrr += rr

        avg_precision /= len(target)
        avg_recall /= len(target)
        mrr /= len(target)

        return {"precision": avg_precision, "recall": avg_recall, "mrr": mrr}


if __name__ == "__main__":
    e = Evaluator()
