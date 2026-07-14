from dataclasses import dataclass


@dataclass
class SearchResult:

    score: float

    text: str

    metadata: dict