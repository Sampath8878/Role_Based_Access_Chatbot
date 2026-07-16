from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchAny,
)

from app.auth.roles import RoleManager


class RoleFilter:
    @staticmethod
    def build(role: str) -> Filter | None:
        normalized_role = RoleManager.normalize_role(role)

        # C-Level may search every department.
        if normalized_role == "c_level":
            return None

        allowed_departments = (
            RoleManager.get_allowed_departments(normalized_role)
        )

        if not allowed_departments:
            raise ValueError(
                f"No department access is configured for role: {role}"
            )

        return Filter(
            must=[
                FieldCondition(
                    key="department",
                    match=MatchAny(
                        any=sorted(allowed_departments)
                    ),
                )
            ]
        )