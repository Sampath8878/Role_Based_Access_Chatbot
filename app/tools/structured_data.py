import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from app.auth.roles import RoleManager


class StructuredDataService:
    """
    Performs exact HR calculations using every row in hr_data.csv.

    This prevents top-k vector retrieval from treating five retrieved
    employee records as the complete employee dataset.
    """

    ALLOWED_ROLES = {
        "hr",
        "c_level",
    }

    NON_HR_BUSINESS_PATTERNS = [
        r"\bfinancial\s+performance\b",
        r"\bfinance\s+performance\b",
        r"\bfinancial\s+report\b",
        r"\brevenue\b",
        r"\bgross\s+margin\b",
        r"\bnet\s+income\b",
        r"\bcash\s+flow\b",
        r"\bmarketing\s+performance\b",
        r"\bmarketing\s+report\b",
        r"\bcampaign\s+performance\b",
        r"\bmarketing\s+roi\b",
        r"\bcustomer\s+acquisition\b",
        r"\bcustomer\s+retention\b",
        r"\btechnical\s+performance\b",
        r"\bsystem\s+performance\b",
        r"\bengineering\s+performance\b",
        r"\btechnical\s+architecture\b",
        r"\bci\s*/?\s*cd\b",
        r"\bmicroservices?\b",
        r"\bdevops\b",
    ]

    HR_AGGREGATION_PATTERNS = [
        r"\bhow\s+many\s+employees\b",
        r"\bnumber\s+of\s+employees\b",
        r"\btotal\s+(number|count)\s+of\s+employees\b",
        r"\btotal\s+employees\b",
        r"\bemployee\s+count\b",
        r"\bheadcount\b",
        r"\bworkforce\s+size\b",

        r"\bdepartment\s+wise\s+count\b",
        r"\bdepartment-wise\s+count\b",
        r"\bdepartment\s+count\b",
        r"\bcount\s+by\s+department\b",
        r"\bcount\s+per\s+department\b",
        r"\bcount\s+for\s+each\s+department\b",
        r"\bemployees?\s+by\s+department\b",
        r"\bemployees?\s+per\s+department\b",
        r"\bemployees?\s+in\s+each\s+department\b",
        r"\bheadcount\s+by\s+department\b",
        r"\bdepartment\s+breakdown\b",

        r"\baverage\s+salary\b",
        r"\bmean\s+salary\b",
        r"\bavg\s+salary\b",
        r"\btotal\s+salary\b",
        r"\btotal\s+payroll\b",
        r"\bhighest\s+salary\b",
        r"\blowest\s+salary\b",
        r"\bhighest\s+paid\b",
        r"\blowest\s+paid\b",
        r"\bsalary\s+by\s+department\b",

        r"\baverage\s+attendance\b",
        r"\battendance\s+by\s+department\b",
        r"\bhighest\s+attendance\b",
        r"\blowest\s+attendance\b",

        r"\baverage\s+performance\s+rating\b",
        r"\bperformance\s+rating\s+by\s+department\b",
        r"\bhighest\s+performance\s+rating\b",
        r"\blowest\s+performance\s+rating\b",

        r"\baverage\s+leave\s+balance\b",
        r"\btotal\s+leave\s+balance\b",
        r"\bleave\s+balance\s+by\s+department\b",

        r"\bnot\s+equal\s+to\s+100\b",
        r"\bdoesn'?t\s+add\s+up\s+to\s+100\b",
        r"\bdoes\s+not\s+add\s+up\s+to\s+100\b",
        r"\bsum\s+to\s+100\b",
        r"\badd\s+up\s+to\s+100\b",
    ]

    NUMERIC_COLUMN_ALIASES: Dict[str, List[str]] = {
        "salary": [
            "salary",
            "salaries",
            "payroll",
            "compensation",
            "highest paid",
            "lowest paid",
        ],
        "attendance_pct": [
            "attendance",
            "attendance percentage",
            "attendance rate",
        ],
        "performance_rating": [
            "performance rating",
            "employee performance",
            "staff performance",
        ],
        "leave_balance": [
            "leave balance",
            "remaining leave",
            "available leave",
        ],
        "leaves_taken": [
            "leaves taken",
            "leave taken",
            "used leave",
        ],
    }

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[2]

        self.hr_csv_path = (
            self.project_root
            / "documents"
            / "hr"
            / "hr_data.csv"
        )

    @staticmethod
    def normalize_text(text: str) -> str:
        return re.sub(
            r"\s+",
            " ",
            text.strip().lower(),
        )

    @staticmethod
    def matches_any(
        question: str,
        patterns: List[str],
    ) -> bool:
        return any(
            re.search(pattern, question)
            for pattern in patterns
        )

    @staticmethod
    def format_number(value: float) -> str:
        if pd.isna(value):
            return "Not available"

        if float(value).is_integer():
            return f"{int(value):,}"

        return f"{value:,.2f}"

    @staticmethod
    def format_percentage(value: float) -> str:
        return f"{value:.2f}%"

    @staticmethod
    def source() -> Dict[str, Any]:
        return {
            "file": "hr_data.csv",
            "department": "hr",
            "chunk_index": None,
            "score": None,
            "source_type": "structured_csv",
        }

    def load_dataframe(self) -> pd.DataFrame:
        if not self.hr_csv_path.exists():
            raise FileNotFoundError(
                f"HR CSV was not found: {self.hr_csv_path}"
            )

        dataframe = pd.read_csv(self.hr_csv_path)

        if dataframe.empty:
            raise ValueError("The HR CSV file is empty.")

        dataframe.columns = [
            str(column).strip().lower()
            for column in dataframe.columns
        ]

        return dataframe

    def can_handle(self, question: str) -> bool:
        normalized_question = self.normalize_text(question)

        if self.matches_any(
            normalized_question,
            self.NON_HR_BUSINESS_PATTERNS,
        ):
            return False

        return self.matches_any(
            normalized_question,
            self.HR_AGGREGATION_PATTERNS,
        )

    @staticmethod
    def detect_operation(question: str) -> str:
        if re.search(
            r"\b(average|avg|mean)\b",
            question,
        ):
            return "average"

        if re.search(
            r"\b(total\s+salary|total\s+payroll|sum)\b",
            question,
        ):
            return "sum"

        if re.search(
            r"\b(highest|maximum|most|top)\b",
            question,
        ):
            return "maximum"

        if re.search(
            r"\b(lowest|minimum|least|bottom)\b",
            question,
        ):
            return "minimum"

        return "count"

    @classmethod
    def detect_numeric_column(
        cls,
        question: str,
    ) -> Optional[str]:
        for column, aliases in cls.NUMERIC_COLUMN_ALIASES.items():
            if any(
                alias in question
                for alias in aliases
            ):
                return column

        return None

    @staticmethod
    def is_department_grouping(question: str) -> bool:
        patterns = [
            r"\bdepartment\s+wise\b",
            r"\bdepartment-wise\b",
            r"\bby\s+department\b",
            r"\bper\s+department\b",
            r"\beach\s+department\b",
            r"\bin\s+each\s+department\b",
            r"\bdepartment\s+breakdown\b",
            r"\bdepartment\s+count\b",
        ]

        return any(
            re.search(pattern, question)
            for pattern in patterns
        )

    @staticmethod
    def detect_department(
        question: str,
        dataframe: pd.DataFrame,
    ) -> Optional[str]:
        if "department" not in dataframe.columns:
            return None

        departments = (
            dataframe["department"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        for department in sorted(
            departments,
            key=len,
            reverse=True,
        ):
            if department.lower() in question:
                return department

        return None

    @staticmethod
    def filter_by_department(
        dataframe: pd.DataFrame,
        department: Optional[str],
    ) -> pd.DataFrame:
        if not department:
            return dataframe

        return dataframe[
            dataframe["department"]
            .astype(str)
            .str.strip()
            .str.lower()
            == department.strip().lower()
        ]

    @staticmethod
    def employee_count(
        dataframe: pd.DataFrame,
    ) -> int:
        if "employee_id" in dataframe.columns:
            return int(
                dataframe["employee_id"]
                .dropna()
                .nunique()
            )

        return int(len(dataframe))

    def department_count_answer(
        self,
        dataframe: pd.DataFrame,
        question: str,
    ) -> str:
        if "department" not in dataframe.columns:
            return (
                "The HR dataset does not contain a department column."
            )

        counts = (
            dataframe["department"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .value_counts()
            .sort_values(
                ascending=False
            )
        )

        total_from_departments = int(counts.sum())
        total_records = self.employee_count(dataframe)

        count_lines = [
            f"- {department}: {int(count):,}"
            for department, count in counts.items()
        ]

        if total_from_departments == total_records:
            validation_message = (
                f"The department counts add up correctly to "
                f"{total_records:,} employees."
            )
        else:
            missing_count = total_records - total_from_departments

            validation_message = (
                f"The department counts total "
                f"{total_from_departments:,}, while the dataset contains "
                f"{total_records:,} employees. The difference is "
                f"{missing_count:,}. This usually means some records have "
                "missing or inconsistent department values."
            )

        if (
            "not equal to 100" in question
            or "doesn't add up" in question
            or "does not add up" in question
        ):
            introduction = (
                "The earlier answer was incorrect because it used only "
                "a small set of retrieved employee chunks instead of "
                "calculating from the complete HR CSV. Using all rows:"
            )
        else:
            introduction = (
                f"The HR dataset contains {total_records:,} employees."
            )

        return (
            f"{introduction}\n\n"
            "Employee count by department:\n"
            + "\n".join(count_lines)
            + f"\n\n{validation_message}"
        )

    @staticmethod
    def employee_summary(
        employee_row: pd.Series,
        numeric_column: str,
    ) -> str:
        full_name = employee_row.get(
            "full_name",
            "Unknown employee",
        )

        employee_id = employee_row.get(
            "employee_id",
            "No ID",
        )

        role = employee_row.get(
            "role",
            "Unknown",
        )

        department = employee_row.get(
            "department",
            "Unknown",
        )

        return (
            f"{full_name} ({employee_id}), "
            f"Role: {role}, Department: {department}"
        )

    def numeric_answer(
        self,
        dataframe: pd.DataFrame,
        question: str,
        numeric_column: str,
        operation: str,
        department: Optional[str],
    ) -> str:
        if numeric_column not in dataframe.columns:
            return (
                f"The HR dataset does not contain the required "
                f"{numeric_column.replace('_', ' ')} column."
            )

        filtered = self.filter_by_department(
            dataframe,
            department,
        ).copy()

        filtered[numeric_column] = pd.to_numeric(
            filtered[numeric_column],
            errors="coerce",
        )

        filtered = filtered.dropna(
            subset=[numeric_column]
        )

        if filtered.empty:
            return (
                f"No valid {numeric_column.replace('_', ' ')} "
                "values matched the request."
            )

        scope = (
            f" in the {department} department"
            if department
            else ""
        )

        label = numeric_column.replace(
            "_",
            " ",
        )

        if self.is_department_grouping(question):
            grouped = filtered.groupby(
                "department"
            )[numeric_column]

            if operation == "sum":
                result = grouped.sum()
                operation_label = "total"

            elif operation == "maximum":
                result = grouped.max()
                operation_label = "maximum"

            elif operation == "minimum":
                result = grouped.min()
                operation_label = "minimum"

            else:
                result = grouped.mean()
                operation_label = "average"

            result = result.sort_values(
                ascending=False
            )

            lines = []

            for group_name, value in result.items():
                formatted = (
                    self.format_percentage(value)
                    if numeric_column == "attendance_pct"
                    else self.format_number(value)
                )

                lines.append(
                    f"- {group_name}: {formatted}"
                )

            return (
                f"The {operation_label} {label} by department is:\n"
                + "\n".join(lines)
            )

        if operation == "sum":
            value = filtered[numeric_column].sum()

            return (
                f"The total {label}{scope} is "
                f"{self.format_number(value)}."
            )

        if operation == "average":
            value = filtered[numeric_column].mean()

            formatted = (
                self.format_percentage(value)
                if numeric_column == "attendance_pct"
                else self.format_number(value)
            )

            return (
                f"The average {label}{scope} is {formatted}."
            )

        if operation == "maximum":
            row_index = filtered[numeric_column].idxmax()
            employee = filtered.loc[row_index]
            value = employee[numeric_column]

            return (
                f"The highest {label}{scope} is "
                f"{self.format_number(value)}. "
                f"Employee: "
                f"{self.employee_summary(employee, numeric_column)}."
            )

        if operation == "minimum":
            row_index = filtered[numeric_column].idxmin()
            employee = filtered.loc[row_index]
            value = employee[numeric_column]

            return (
                f"The lowest {label}{scope} is "
                f"{self.format_number(value)}. "
                f"Employee: "
                f"{self.employee_summary(employee, numeric_column)}."
            )

        return (
            "The requested calculation could not be completed."
        )

    def calculate(
        self,
        dataframe: pd.DataFrame,
        question: str,
    ) -> str:
        if self.is_department_grouping(question):
            numeric_column = self.detect_numeric_column(
                question
            )

            if numeric_column is None:
                return self.department_count_answer(
                    dataframe,
                    question,
                )

        department = self.detect_department(
            question,
            dataframe,
        )

        numeric_column = self.detect_numeric_column(
            question
        )

        operation = self.detect_operation(
            question
        )

        if numeric_column:
            return self.numeric_answer(
                dataframe=dataframe,
                question=question,
                numeric_column=numeric_column,
                operation=operation,
                department=department,
            )

        filtered = self.filter_by_department(
            dataframe,
            department,
        )

        count = self.employee_count(
            filtered
        )

        if department:
            return (
                f"There are {count:,} employees in the "
                f"{department} department, based on all rows "
                "in hr_data.csv."
            )

        return (
            f"The company has {count:,} employees, based on all "
            "employee records in hr_data.csv."
        )

    def answer(
        self,
        role: str,
        question: str,
    ) -> Optional[Dict[str, Any]]:
        normalized_role = RoleManager.normalize_role(
            role
        )

        normalized_question = self.normalize_text(
            question
        )

        if not self.can_handle(
            normalized_question
        ):
            return None

        if normalized_role not in self.ALLOWED_ROLES:
            return {
                "answer": (
                    "Access denied. HR employee data is available "
                    "only to the HR Team and C-Level Executives."
                ),
                "sources": [],
                "authorized": False,
                "response_type": "access_denied",
            }

        try:
            dataframe = self.load_dataframe()

            answer = self.calculate(
                dataframe,
                normalized_question,
            )

            return {
                "answer": answer,
                "sources": [
                    self.source()
                ],
                "authorized": True,
                "response_type": "structured_data",
            }

        except (
            FileNotFoundError,
            ValueError,
            KeyError,
            pd.errors.ParserError,
        ) as error:
            return {
                "answer": (
                    "The HR dataset could not be analyzed. "
                    f"Technical details: {error}"
                ),
                "sources": [],
                "authorized": True,
                "response_type": "structured_error",
            }