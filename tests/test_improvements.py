from app.rag.chatbot import FinSolveChatbot


def test_question(
    chatbot: FinSolveChatbot,
    role: str,
    question: str,
) -> None:
    result = chatbot.chat(
        role=role,
        question=question,
        session_id=f"test_{role}",
    )

    print("=" * 80)
    print(f"ROLE: {role}")
    print(f"QUESTION: {question}")
    print("-" * 80)
    print(result["answer"])
    print()
    print(
        "Response type:",
        result.get("response_type"),
    )
    print(
        "Authorized:",
        result.get("authorized"),
    )
    print(
        "Sources:",
        result.get("sources"),
    )
    print()


def main() -> None:
    chatbot = FinSolveChatbot()

    tests = [
        # Employee should access only General.
        (
            "employee",
            "What is the leave policy?",
        ),
        (
            "employee",
            "What was the Q4 revenue?",
        ),

        # Finance should access only Finance.
        (
            "finance",
            "What was the Q4 revenue?",
        ),
        (
            "finance",
            "What is the leave policy?",
        ),

        # HR structured analytics.
        (
            "hr",
            "How many employees are there?",
        ),
        (
            "hr",
            "Show employee count by department.",
        ),
        (
            "hr",
            "What is the average salary?",
        ),
        (
            "hr",
            "What is the average salary by department?",
        ),
        (
            "hr",
            "Who has the highest salary?",
        ),
        (
            "hr",
            "What is the average attendance by department?",
        ),

        # Marketing should access only Marketing.
        (
            "marketing",
            "Summarize the Q4 marketing performance.",
        ),
        (
            "marketing",
            "What was the Q4 company revenue?",
        ),

        # Engineering should access only Engineering.
        (
            "engineering",
            "Explain the CI/CD pipeline.",
        ),
        (
            "engineering",
            "What is the employee leave policy?",
        ),

        # C-Level should access all data.
        (
            "c_level",
            "How many employees are there?",
        ),
        (
            "c_level",
            "What was the Q4 revenue?",
        ),
        (
            "c_level",
            "Explain the company leave policy.",
        ),
        (
            "c_level",
            "Explain the engineering architecture.",
        ),
    ]

    for role, question in tests:
        test_question(
            chatbot,
            role,
            question,
        )


if __name__ == "__main__":
    main()