from typing import Dict, List, Set


class RoleManager:
    """
    Central role and authorization configuration.

    Access rules:
    - Employee: General only
    - Finance: Finance only
    - HR: HR only
    - Marketing: Marketing only
    - Engineering: Engineering only
    - C-Level: All departments
    """

    ROLE_DISPLAY_TO_INTERNAL: Dict[str, str] = {
        "Employee": "employee",
        "Finance Team": "finance",
        "HR Team": "hr",
        "Marketing Team": "marketing",
        "Engineering Department": "engineering",
        "C-Level Executive": "c_level",
    }

    INTERNAL_TO_DISPLAY: Dict[str, str] = {
        internal: display
        for display, internal in ROLE_DISPLAY_TO_INTERNAL.items()
    }

    ROLE_DESCRIPTIONS: Dict[str, str] = {
        "employee": (
            "Access is limited to general company policies, events, "
            "guidelines and FAQs."
        ),
        "finance": (
            "Access is limited to Finance Department documents."
        ),
        "hr": (
            "Access is limited to HR data and HR analytics."
        ),
        "marketing": (
            "Access is limited to Marketing Department documents."
        ),
        "engineering": (
            "Access is limited to Engineering Department documents."
        ),
        "c_level": (
            "Full access to Finance, HR, Marketing, Engineering "
            "and General company information."
        ),
    }

    ROLE_DEPARTMENTS: Dict[str, Set[str]] = {
        "employee": {"general"},
        "finance": {"finance"},
        "hr": {"hr"},
        "marketing": {"marketing"},
        "engineering": {"engineering"},
        "c_level": {
            "general",
            "finance",
            "hr",
            "marketing",
            "engineering",
        },
    }

    @classmethod
    def get_display_roles(cls) -> List[str]:
        return list(cls.ROLE_DISPLAY_TO_INTERNAL.keys())

    @classmethod
    def get_internal_role(cls, display_role: str) -> str:
        if display_role not in cls.ROLE_DISPLAY_TO_INTERNAL:
            raise ValueError(f"Unknown role: {display_role}")

        return cls.ROLE_DISPLAY_TO_INTERNAL[display_role]

    @classmethod
    def get_display_role(cls, internal_role: str) -> str:
        normalized_role = cls.normalize_role(internal_role)

        return cls.INTERNAL_TO_DISPLAY.get(
            normalized_role,
            normalized_role.replace("_", " ").title(),
        )

    @classmethod
    def get_description(cls, internal_role: str) -> str:
        normalized_role = cls.normalize_role(internal_role)

        return cls.ROLE_DESCRIPTIONS.get(
            normalized_role,
            "No role description is available.",
        )

    @classmethod
    def normalize_role(cls, role: str) -> str:
        if not role:
            raise ValueError("Role cannot be empty.")

        normalized = (
            role.strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        aliases = {
            "finance_team": "finance",
            "hr_team": "hr",
            "marketing_team": "marketing",
            "engineering_department": "engineering",
            "engineering_team": "engineering",
            "employee_level": "employee",
            "c_level_executive": "c_level",
            "c_level_executives": "c_level",
            "c_level": "c_level",
            "executive": "c_level",
            "ceo": "c_level",
        }

        return aliases.get(normalized, normalized)

    @classmethod
    def is_valid_internal_role(cls, role: str) -> bool:
        try:
            normalized_role = cls.normalize_role(role)
        except ValueError:
            return False

        return normalized_role in cls.INTERNAL_TO_DISPLAY

    @classmethod
    def get_allowed_departments(cls, role: str) -> Set[str]:
        normalized_role = cls.normalize_role(role)

        return cls.ROLE_DEPARTMENTS.get(
            normalized_role,
            set(),
        )

    @classmethod
    def can_access_department(
        cls,
        role: str,
        department: str,
    ) -> bool:
        normalized_role = cls.normalize_role(role)
        normalized_department = (
            department.strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        return (
            normalized_department
            in cls.get_allowed_departments(normalized_role)
        )