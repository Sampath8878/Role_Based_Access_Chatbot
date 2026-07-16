import re

from app.auth.roles import RoleManager


class QueryExpander:
    """
    Adds domain-specific keywords to broad or summary questions.

    This helps Qdrant retrieve relevant chunks for questions such as:

    - Summarize the Q4 marketing performance.
    - Summarize the company's financial performance in 2024.
    """

    @staticmethod
    def normalize(question: str) -> str:
        return re.sub(
            r"\s+",
            " ",
            question.strip(),
        )

    @staticmethod
    def is_summary_question(question: str) -> bool:
        normalized = question.lower()

        indicators = [
            "summarize",
            "summary",
            "overview",
            "performance",
            "highlights",
            "review",
            "explain",
            "describe",
        ]

        return any(
            indicator in normalized
            for indicator in indicators
        )

    @staticmethod
    def detect_quarter(question: str) -> str | None:
        normalized = question.lower()

        quarter_patterns = {
            "Q1": [
                r"\bq1\b",
                r"\bfirst\s+quarter\b",
            ],
            "Q2": [
                r"\bq2\b",
                r"\bsecond\s+quarter\b",
            ],
            "Q3": [
                r"\bq3\b",
                r"\bthird\s+quarter\b",
            ],
            "Q4": [
                r"\bq4\b",
                r"\bfourth\s+quarter\b",
            ],
        }

        for quarter, patterns in quarter_patterns.items():
            if any(
                re.search(pattern, normalized)
                for pattern in patterns
            ):
                return quarter

        return None

    @staticmethod
    def detect_year(question: str) -> str | None:
        match = re.search(
            r"\b(20\d{2})\b",
            question,
        )

        if match:
            return match.group(1)

        return None

    @classmethod
    def expand(
        cls,
        question: str,
        role: str,
    ) -> str:
        cleaned_question = cls.normalize(question)

        normalized_role = RoleManager.normalize_role(role)

        quarter = cls.detect_quarter(
            cleaned_question
        )

        year = cls.detect_year(
            cleaned_question
        )

        time_keywords = []

        if quarter:
            time_keywords.append(quarter)

        if year:
            time_keywords.append(year)

        if normalized_role == "finance":
            domain_keywords = [
                "financial report",
                "quarterly revenue",
                "income",
                "gross margin",
                "marketing spend",
                "vendor costs",
                "expenses",
                "cash flow",
                "risk mitigation",
                "financial performance",
            ]

        elif normalized_role == "marketing":
            domain_keywords = [
                "marketing report",
                "campaign performance",
                "campaign spend",
                "customer acquisition",
                "conversion",
                "ROI",
                "revenue projection",
                "digital marketing",
                "B2B initiatives",
                "customer retention",
                "performance highlights",
                "recommendations",
            ]

        elif normalized_role == "engineering":
            domain_keywords = [
                "technical architecture",
                "microservices",
                "CI/CD pipeline",
                "security model",
                "DevOps",
                "monitoring",
                "compliance",
                "development standards",
                "technical roadmap",
            ]

        elif normalized_role == "hr":
            domain_keywords = [
                "employee data",
                "attendance",
                "salary",
                "leave",
                "performance",
                "department",
                "workforce",
                "HR analytics",
            ]

        elif normalized_role == "employee":
            domain_keywords = [
                "employee handbook",
                "company policy",
                "leave",
                "working hours",
                "code of conduct",
                "onboarding",
                "reimbursement",
                "FAQ",
            ]

        elif normalized_role == "c_level":
            domain_keywords = [
                "company performance",
                "finance",
                "marketing",
                "HR",
                "engineering",
                "general policy",
                "business risks",
                "department highlights",
            ]

        else:
            domain_keywords = []

        if not cls.is_summary_question(
            cleaned_question
        ):
            return cleaned_question

        expanded_parts = [
            cleaned_question,
            *time_keywords,
            *domain_keywords,
        ]

        return " | ".join(
            expanded_parts
        )