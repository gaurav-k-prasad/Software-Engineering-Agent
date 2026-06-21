import warnings
from utils.constants import BATCH_SIZE
from tqdm import tqdm

warnings.filterwarnings("ignore")

from pathlib import Path
from chunking import chunk_files
from embedding.main import embed_and_store, search
from utils.embed_input import datadict2embed_input, jsonl2datadict

curr_dir = Path.cwd() / "data" / "test-repo"
with open("output.jsonl", "w") as f:
    chunk_files(curr_dir, f)

with open("output.jsonl", "r") as f:
    lines = f.readlines()
    n_chunks = len(lines)
    lines = list(map(jsonl2datadict, lines))

batch: list[str] = []
batches: list[list[str]] = []

print("Forming Batches: ")
for i in tqdm(range(n_chunks)):
    embed_input = datadict2embed_input(lines[i])
    batch.append(embed_input)

    if len(batch) == BATCH_SIZE or i == n_chunks - 1:
        batches.append(batch)
        batch = []

print("Embedding and saving batches: ")
for batch in tqdm(batches):
    embed_and_store(batch)

while True:
    try:
        query = input("Query: ")
        distances, indices = search(query)

        print(indices[0])
        print(distances[0])

        index = int(input())
        while index != -1:
            print(datadict2embed_input(lines[int(indices[0][index])]))
            print("=" * 40)
            index = int(input())
    except Exception:
        continue