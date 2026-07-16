from app.auth.roles import RoleManager
from app.rag.chatbot import FinSolveChatbot


def print_sources(sources) -> None:
    if not sources:
        print("Sources: None")
        return

    print("\nSources:")

    for index, source in enumerate(sources, start=1):
        print(
            f"{index}. {source.get('file')} | "
            f"Department: {source.get('department')} | "
            f"Score: {source.get('score')}"
        )


def main() -> None:
    chatbot = FinSolveChatbot()
    session_id = "terminal_test"

    print("=" * 70)
    print("FinSolve Role-Based AI Assistant")
    print("=" * 70)

    print("\nAvailable roles:")

    for display_role in RoleManager.get_display_roles():
        internal_role = RoleManager.get_internal_role(display_role)

        print(
            f"- {display_role}: {internal_role}"
        )

    print("\nCommands:")
    print("- Type 'clear' to clear conversation memory.")
    print("- Type 'exit' to close the application.")

    while True:
        print("\n" + "-" * 70)

        role_input = input(
            "Role: "
        ).strip()

        if role_input.lower() == "exit":
            break

        try:
            normalized_role = RoleManager.normalize_role(role_input)
        except ValueError as error:
            print(error)
            continue

        if not RoleManager.is_valid_internal_role(normalized_role):
            print(
                "Invalid role. Use employee, finance, marketing, "
                "hr, engineering or c_level."
            )
            continue

        question = input(
            "Question: "
        ).strip()

        if question.lower() == "exit":
            break

        if question.lower() == "clear":
            chatbot.clear_memory(session_id)

            print("Conversation memory cleared.")
            continue

        result = chatbot.chat(
            role=normalized_role,
            question=question,
            session_id=session_id,
        )

        print("\nAnswer:")
        print(result["answer"])

        print_sources(result.get("sources", []))

    print("\nApplication closed.")


if __name__ == "__main__":
    main()