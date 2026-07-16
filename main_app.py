import uuid

import streamlit as st

from app.auth.roles import RoleManager
from app.rag.chatbot import FinSolveChatbot
from app.ui.chat import (
    add_assistant_message,
    add_user_message,
    clear_chat_state,
    initialize_chat_state,
    render_chat_history,
    render_sources,
    show_welcome_message,
)
from app.ui.sidebar import render_sidebar


st.set_page_config(
    page_title="FinSolve Role-Based AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="Initializing AI assistant...")
def get_chatbot() -> FinSolveChatbot:
    return FinSolveChatbot()


def create_session_id() -> str:
    return str(uuid.uuid4())


def initialize_application_state() -> None:
    initialize_chat_state()

    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = create_session_id()

    if "previous_role" not in st.session_state:
        st.session_state.previous_role = None


def reset_conversation(
    chatbot: FinSolveChatbot,
) -> None:
    current_session_id = st.session_state.chat_session_id

    chatbot.clear_memory(current_session_id)

    clear_chat_state()

    st.session_state.chat_session_id = create_session_id()


def main() -> None:
    initialize_application_state()

    chatbot = get_chatbot()

    selected_role, clear_requested = render_sidebar()

    if (
        st.session_state.previous_role is not None
        and st.session_state.previous_role != selected_role
    ):
        reset_conversation(chatbot)

    st.session_state.previous_role = selected_role

    if clear_requested:
        reset_conversation(chatbot)
        st.rerun()

    display_role = RoleManager.get_display_role(selected_role)

    st.title("FinSolve Enterprise AI Assistant")

    st.caption(
        "Secure role-based retrieval using Qdrant, "
        "HuggingFace embeddings and Groq."
    )

    st.divider()

    # Removed the right-side access-status box.
    st.markdown(
        f"### Chatting as: **{display_role}**"
    )

    show_welcome_message(display_role)

    render_chat_history()

    question = st.chat_input(
        "Ask a question about FinSolve company documents..."
    )

    if not question:
        return

    add_user_message(question)

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(
            "Searching authorized documents and generating an answer..."
        ):
            try:
                result = chatbot.chat(
                    role=selected_role,
                    question=question,
                    session_id=st.session_state.chat_session_id,
                )

                answer = result.get(
                    "answer",
                    "No answer was generated.",
                )

                sources = result.get(
                    "sources",
                    [],
                )

                st.markdown(answer)

                render_sources(sources)

                add_assistant_message(
                    content=answer,
                    sources=sources,
                )

            except Exception as error:
                error_message = (
                    "The assistant encountered an error. "
                    f"Details: {error}"
                )

                st.error(error_message)

                add_assistant_message(
                    content=error_message,
                    sources=[],
                )


if __name__ == "__main__":
    main()