import warnings

from code_retriever import DocumentStore
from code_retriever import HybridSearch

warnings.filterwarnings("ignore")

from utils.constants import BATCH_SIZE
from pathlib import Path
from chunking import PythonChunker
from code_retriever import (
    FAISS,
    HybridSearch,
    BM25_Plus,
    ReciprocalRankFusion,
)
from evaluator import Evaluator, SearchQueryData
from utils.embed_input import datadict2embed_input, jsonl2datadict
from pprint import pprint
import json

py_chunker = PythonChunker()
curr_dir = Path.cwd() / "data" / "test-repo"
print(curr_dir)
with open("output.jsonl", "w") as f:
    py_chunker.chunk_files(curr_dir, f)

with open("output.jsonl", "r") as f:
    lines = f.readlines()
    n_chunks = len(lines)
    metadatas = list(map(jsonl2datadict, lines))

target: list[SearchQueryData] = []
with open("./rag_eval_dataset_symbolic.jsonl", "r") as f:
    for line in f.readlines():
        target.append(json.loads(line))


texts: list[str] = []
chunk_ids: list[str] = []
doc_store = DocumentStore()

for i in range(n_chunks):
    embed_input = datadict2embed_input(metadatas[i])
    chunk_ids.append(metadatas[i].chunk_id)
    doc_store.insert(metadatas[i])
    texts.append(embed_input)

dense = FAISS(batch_size=BATCH_SIZE)
bm25 = BM25_Plus()

hybrid_search = HybridSearch([dense, bm25], ReciprocalRankFusion())
hybrid_search.fit(texts, chunk_ids)

e = Evaluator()
# print(e.evaluate(1, lambda x, y: doc_store.get([item.chunk_id for item in hybrid_search.search(x, y)]), target), "\n\n")
# print(e.evaluate(2, lambda x, y: doc_store.get([item.chunk_id for item in hybrid_search.search(x, y)]), target), "\n\n")
# print(e.evaluate(5, lambda x, y: doc_store.get([item.chunk_id for item in hybrid_search.search(x, y)]), target), "\n\n")
# print(e.evaluate(10, lambda x, y: doc_store.get([item.chunk_id for item in hybrid_search.search(x, y)]), target), "\n\n")
# print(e.evaluate(20, lambda x, y: doc_store.get([item.chunk_id for item in hybrid_search.search(x, y)]), target), "\n\n")

while True:
    try:
        q = input("Enter your query: ")
        if q == "q":
            break

        hybrid_result = hybrid_search.search(q, 5)
        ids = [res.chunk_id for res in hybrid_result]
        res = doc_store.get(ids)

        for r in res:
            pprint(r)
    except Exception as e:
        print(e)
