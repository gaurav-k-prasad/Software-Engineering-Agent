import warnings

warnings.filterwarnings("ignore")

import torch
from evaluator import Evaluator
from core import RetrievalPipeline
import json
from code_retriever import (
    FAISS,
    BM25_Plus,
    Reranker,
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
reranker = Reranker(device=device)
chunk_store = ChunkStore()
python_chunker = PythonChunker()

retriever_pipeline = RetrievalPipeline(
    search_strategy, reranker, chunk_store, python_chunker
)

retriever_pipeline.index_repository("data/test-repo", "output.jsonl")
# retriever_pipeline.search("user controller", 8)

e = Evaluator()
with open("rag_eval_dataset_natural_language.jsonl") as f:
    target = [json.loads(line) for line in f.readlines()]

print(e.evaluate(8, retriever_pipeline.search, target))
