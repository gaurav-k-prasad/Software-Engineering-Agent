import warnings

warnings.filterwarnings("ignore")

from collections import defaultdict
from embedding import BM25_Plus
from utils.constants import BATCH_SIZE, NEAREST_NEIGHBOUR_COUNT
from tqdm import tqdm
from pathlib import Path
from chunking import chunk_files
from embedding import FAISS
from evaluator import Evaluator, SearchQueryData
from utils.embed_input import datadict2embed_input, jsonl2datadict
from pprint import pprint
import json

curr_dir = Path.cwd() / "data" / "test-repo"
print(curr_dir)
with open("output.jsonl", "w") as f:
    chunk_files(curr_dir, f)

with open("output.jsonl", "r") as f:
    lines = f.readlines()
    n_chunks = len(lines)
    metadatas = list(map(jsonl2datadict, lines))

target: list[SearchQueryData] = []
with open("./rag_eval_dataset_symbolic.jsonl", "r") as f:
    for line in f.readlines():
        target.append(json.loads(line))


texts: list[str] = []
for i in range(n_chunks):
    embed_input = datadict2embed_input(metadatas[i])
    texts.append(embed_input)

dense = FAISS(batch_size=BATCH_SIZE)
dense.embed_and_store(texts, metadatas)

bm25 = BM25_Plus()
bm25.fit_finalize(texts, list(range(len(texts))), metadatas)

while True:
    try:
        q = input()
        if q == "q":
            break

        dense_results = dense.search(q, 20)
        bm25_results = bm25.search(q, 20)
        scores: defaultdict[str, float] = defaultdict(float)

        for rank, doc in enumerate(dense_results, start=1):
            scores[doc.chunk_id] += 1 / (60 + rank)

        for rank, doc in enumerate(bm25_results, start=1):
            scores[doc.chunk_id] += 1 / (60 + rank)

        sorted_docs = sorted(scores.items(), key=lambda x: -x[1])

        pprint(sorted_docs)

    except Exception:
        continue
