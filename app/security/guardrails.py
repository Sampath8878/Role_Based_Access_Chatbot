import re
from dataclasses import dataclass
from typing import Optional, Set

from app.auth.roles import RoleManager


@dataclass
class GuardrailResult:
    allowed: bool
    message: Optional[str] = None
    requested_department: Optional[str] = None
    reason: Optional[str] = None


class SecurityGuardrail:
    """
    Checks the user's question before retrieval or LLM generation.

    It prevents:
    - Role impersonation
    - Prompt injection
    - Cross-department access attempts
    - Requests for sensitive HR employee-level information
    """

    PROMPT_INJECTION_PATTERNS = [
        r"\bignore\s+(all\s+)?previous\s+instructions\b",
        r"\bignore\s+(all\s+)?system\s+instructions\b",
        r"\bforget\s+(all\s+)?previous\s+instructions\b",
        r"\bbypass\s+(the\s+)?role\b",
        r"\bbypass\s+(the\s+)?access\b",
        r"\bbypass\s+(the\s+)?security\b",
        r"\bdisable\s+(the\s+)?security\b",
        r"\bdisable\s+(the\s+)?role\s+restrictions\b",
        r"\bpretend\s+(that\s+)?i\s+am\b",
        r"\bpretend\s+i'?m\b",
        r"\bact\s+as\s+(an?\s+)?(admin|administrator|ceo|executive)\b",
        r"\byou\s+are\s+now\s+(an?\s+)?(admin|administrator|ceo)\b",
        r"\bmake\s+me\s+(an?\s+)?(admin|administrator|ceo)\b",
        r"\bmy\s+role\s+is\s+now\b",
        r"\bshow\s+your\s+system\s+prompt\b",
        r"\breveal\s+your\s+instructions\b",
    ]

    FINANCE_PATTERNS = [
        r"\brevenue\b",
        r"\bgross\s+margin\b",
        r"\bnet\s+income\b",
        r"\boperating\s+income\b",
        r"\bcash\s+flow\b",
        r"\bvendor\s+costs?\b",
        r"\bfinancial\s+performance\b",
        r"\bfinancial\s+report\b",
        r"\bfinancial\s+summary\b",
        r"\bquarterly\s+financial\b",
        r"\bcompany\s+finances?\b",
        r"\bexpense\s+breakdown\b",
    ]

    MARKETING_PATTERNS = [
        r"\bmarketing\s+performance\b",
        r"\bmarketing\s+report\b",
        r"\bmarketing\s+summary\b",
        r"\bmarketing\s+campaigns?\b",
        r"\bcampaign\s+performance\b",
        r"\bcampaign\s+budget\b",
        r"\bcustomer\s+acquisition\b",
        r"\bcustomer\s+retention\b",
        r"\bconversion\s+rate\b",
        r"\bmarketing\s+roi\b",
        r"\bdigital\s+marketing\b",
        r"\bb2b\s+initiatives?\b",
    ]

    ENGINEERING_PATTERNS = [
        r"\btechnical\s+architecture\b",
        r"\bsystem\s+architecture\b",
        r"\bmicroservices?\b",
        r"\bci\s*/?\s*cd\b",
        r"\bdeployment\s+pipeline\b",
        r"\bdevops\b",
        r"\bmonitoring\s+architecture\b",
        r"\bengineering\s+process\b",
        r"\bdevelopment\s+standards?\b",
        r"\bgdpr\s+compliance\b",
        r"\bdpdp\s+compliance\b",
        r"\bpci[\s-]?dss\b",
        r"\bblockchain\s+roadmap\b",
        r"\btechnical\s+roadmap\b",
    ]

    HR_SENSITIVE_PATTERNS = [
        r"\bemployee\s+salaries\b",
        r"\bemployees?['’]?\s+salaries\b",
        r"\bsalary\s+list\b",
        r"\bshow\s+(all\s+)?salaries\b",
        r"\bhighest\s+salary\b",
        r"\blowest\s+salary\b",
        r"\baverage\s+salary\b",
        r"\btotal\s+payroll\b",
        r"\bpayroll\s+data\b",
        r"\bemployee\s+attendance\b",
        r"\battendance\s+records?\b",
        r"\bperformance\s+ratings?\b",
        r"\bemployee\s+records?\b",
        r"\bemployee\s+count\b",
        r"\btotal\s+(number|count)\s+of\s+employees\b",
        r"\bhow\s+many\s+employees\b",
        r"\bheadcount\b",
        r"\bworkforce\s+size\b",
    ]

    GENERAL_PATTERNS = [
        r"\bleave\s+policy\b",
        r"\bannual\s+leave\b",
        r"\bcasual\s+leave\b",
        r"\bworking\s+hours\b",
        r"\bdress\s+code\b",
        r"\bonboarding\s+process\b",
        r"\breimbursement\s+policy\b",
        r"\bcode\s+of\s+conduct\b",
        r"\bemployee\s+handbook\b",
        r"\bcompany\s+policy\b",
        r"\bcompany\s+policies\b",
        r"\bcompany\s+events?\b",
        r"\bfaq\b",
    ]

    @staticmethod
    def normalize_question(question: str) -> str:
        return re.sub(
            r"\s+",
            " ",
            question.strip().lower(),
        )

    @staticmethod
    def matches_any(
        question: str,
        patterns: list[str],
    ) -> bool:
        return any(
            re.search(pattern, question)
            for pattern in patterns
        )

    def contains_prompt_injection(
        self,
        question: str,
    ) -> bool:
        return self.matches_any(
            question,
            self.PROMPT_INJECTION_PATTERNS,
        )

    def detect_requested_department(
        self,
        question: str,
    ) -> Optional[str]:
        """
        Returns the most likely requested department.

        HR-sensitive checks occur first because words such as
        employee and salary must not be treated as General data.
        """

        if self.matches_any(
            question,
            self.HR_SENSITIVE_PATTERNS,
        ):
            return "hr"

        if self.matches_any(
            question,
            self.FINANCE_PATTERNS,
        ):
            return "finance"

        if self.matches_any(
            question,
            self.MARKETING_PATTERNS,
        ):
            return "marketing"

        if self.matches_any(
            question,
            self.ENGINEERING_PATTERNS,
        ):
            return "engineering"

        if self.matches_any(
            question,
            self.GENERAL_PATTERNS,
        ):
            return "general"

        return None

    @staticmethod
    def build_access_denied_message(
        department: Optional[str],
    ) -> str:
        department_names = {
            "finance": "Finance",
            "hr": "HR",
            "marketing": "Marketing",
            "engineering": "Engineering",
            "general": "General",
        }

        if department:
            display_department = department_names.get(
                department,
                department.title(),
            )

            return (
                f"Access denied. Your current role does not have "
                f"permission to access {display_department} information."
            )

        return (
            "Access denied. This request attempts to bypass the "
            "role-based access restrictions."
        )

    def validate(
        self,
        role: str,
        question: str,
    ) -> GuardrailResult:
        normalized_role = RoleManager.normalize_role(role)

        normalized_question = self.normalize_question(
            question
        )

        if self.contains_prompt_injection(
            normalized_question
        ):
            return GuardrailResult(
                allowed=False,
                message=(
                    "Access denied. Role impersonation and attempts "
                    "to bypass access restrictions are not allowed."
                ),
                requested_department=None,
                reason="prompt_injection",
            )

        requested_department = (
            self.detect_requested_department(
                normalized_question
            )
        )

        # Unknown or general conversational questions continue to RAG.
        if requested_department is None:
            return GuardrailResult(
                allowed=True,
                requested_department=None,
                reason="no_restricted_intent_detected",
            )

        allowed_departments: Set[str] = (
            RoleManager.get_allowed_departments(
                normalized_role
            )
        )

        if requested_department not in allowed_departments:
            return GuardrailResult(
                allowed=False,
                message=self.build_access_denied_message(
                    requested_department
                ),
                requested_department=requested_department,
                reason="cross_department_access",
            )

        return GuardrailResult(
            allowed=True,
            requested_department=requested_department,
            reason="authorized_department",
        )