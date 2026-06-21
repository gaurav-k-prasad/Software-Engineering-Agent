import dataclasses
import json
from typing import IO, Any


def chunks2jsonl(chunks: list[Any], file: IO[str] | None):
    if file is None:
        raise ValueError("No file stream found")
    
    for chunk in chunks:
        file.write(json.dumps(dataclasses.asdict(chunk)) + "\n")
