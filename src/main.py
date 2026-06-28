import warnings

warnings.filterwarnings("ignore")

import torch
from evaluator import Evaluator
from core import RetrievalPipeline
import json
from code_retriever import (
    FAISS,
    BM25_Plus,
    RerankerLocal,
    ChunkStore,
    HybridSearch,
    ReciprocalRankFusion,
)
from chunker import PythonChunker

device = "cuda" if torch.cuda.is_available() else "cpu"

faiss = FAISS(device=device)
bm25 = BM25_Plus()
fusion_strategy = ReciprocalRankFusion()
search_strategy = HybridSearch([faiss, bm25], fusion_strategy)
reranker = RerankerLocal(device=device)
chunk_store = ChunkStore()
python_chunker = PythonChunker()

retriever_pipeline = RetrievalPipeline(
    search_strategy, reranker, chunk_store, python_chunker
)

retriever_pipeline.index_repository("data/test-repo", "output.jsonl")
res = retriever_pipeline.search("user controller", 8)
for r in res:
    print(r.qualified_name, r.name, r.file_name)

# print(e.evaluate(8, retriever_pipeline.search, target))
