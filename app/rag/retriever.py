from typing import Any, Dict, List

from app.qdrant.search import QdrantSearcher
from app.rag.query_expander import QueryExpander


class Retriever:
    def __init__(self) -> None:
        self.searcher = QdrantSearcher()

    @staticmethod
    def point_to_context(
        point: Any,
    ) -> Dict[str, Any]:
        payload = point.payload or {}

        return {
            "text": payload.get(
                "text",
                "",
            ),
            "score": float(
                point.score
            ),
            "department": payload.get(
                "department",
                "unknown",
            ),
            "file_name": payload.get(
                "file_name",
                "unknown",
            ),
            "allowed_roles": payload.get(
                "allowed_roles",
                [],
            ),
            "metadata": payload,
            "point_id": str(
                point.id
            ),
        }

    def retrieve(
        self,
        question: str,
        role: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        expanded_question = QueryExpander.expand(
            question=question,
            role=role,
        )

        original_points = self.searcher.search(
            question=question,
            role=role,
            limit=max(top_k, 5),
        )

        all_points = list(
            original_points
        )

        if expanded_question != question:
            expanded_points = self.searcher.search(
                question=expanded_question,
                role=role,
                limit=max(top_k + 2, 7),
            )

            all_points.extend(
                expanded_points
            )

        merged_points: Dict[str, Any] = {}

        for point in all_points:
            point_id = str(
                point.id
            )

            current_point = merged_points.get(
                point_id
            )

            if (
                current_point is None
                or point.score > current_point.score
            ):
                merged_points[point_id] = point

        sorted_points = sorted(
            merged_points.values(),
            key=lambda point: point.score,
            reverse=True,
        )

        selected_points = sorted_points[
            :top_k
        ]

        return [
            self.point_to_context(point)
            for point in selected_points
        ]