from transformers import AutoModel
import faiss
import gc
from utils.constants import DIMENSIONS, CODE_MAX_LENGTH, NEAREST_NEIGHBOUR_COUNT

model = AutoModel.from_pretrained(
    "jinaai/jina-embeddings-v2-base-code", trust_remote_code=True
)
index = faiss.IndexHNSWFlat(DIMENSIONS, 32, faiss.METRIC_L2)


def embed_and_store(data: list[str]):
    embeddings = model.encode(
        data,
        max_length=CODE_MAX_LENGTH,
    )

    index.add(embeddings)

def search(query: str):
    query_vector = model.encode(
        [query],
        max_length=CODE_MAX_LENGTH,
    )

    distances, indices = index.search(query_vector, k=NEAREST_NEIGHBOUR_COUNT)

    return distances, indices