from dataclasses import dataclass
from typing import List, Dict


@dataclass
class DocumentChunk:

    point_id: str

    text: str

    embedding: List[float]

    metadata: Dict