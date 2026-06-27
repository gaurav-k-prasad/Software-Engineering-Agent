from dataclasses import dataclass


@dataclass
class SearchResult:
    chunk_id: str
    score: float
