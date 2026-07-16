from typing import Any, Dict, List

import streamlit as st


def initialize_chat_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = "streamlit_default"

    if "message_role" not in st.session_state:
        st.session_state.message_role = None


def clear_chat_state() -> None:
    st.session_state.messages = []


def add_user_message(content: str) -> None:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": content,
            "sources": [],
        }
    )


def add_assistant_message(
    content: str,
    sources: List[Dict[str, Any]] | None = None,
) -> None:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": content,
            "sources": sources or [],
        }
    )


def render_sources(sources: List[Dict[str, Any]]) -> None:
    if not sources:
        return

    unique_sources = []
    seen = set()

    for source in sources:
        file_name = source.get("file") or source.get(
            "file_name",
            "Unknown document",
        )

        department = source.get(
            "department",
            "Unknown department",
        )

        chunk_index = source.get("chunk_index")
        score = source.get("score")

        unique_key = (
            file_name,
            department,
            chunk_index,
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        unique_sources.append(
            {
                "file": file_name,
                "department": department,
                "chunk_index": chunk_index,
                "score": score,
            }
        )

    with st.expander(
        f"Sources ({len(unique_sources)})",
        expanded=False,
    ):
        for index, source in enumerate(unique_sources, start=1):
            st.markdown(
                f"**{index}. {source['file']}**"
            )

            st.write(
                f"Department: {source['department']}"
            )

            if source["chunk_index"] is not None:
                st.write(
                    f"Chunk: {source['chunk_index']}"
                )

            if source["score"] is not None:
                try:
                    st.write(
                        f"Similarity score: "
                        f"{float(source['score']):.4f}"
                    )
                except (TypeError, ValueError):
                    pass

            st.divider()


def render_chat_history() -> None:
    for message in st.session_state.messages:
        message_role = message.get("role", "assistant")

        with st.chat_message(message_role):
            st.markdown(
                message.get("content", "")
            )

            if message_role == "assistant":
                render_sources(
                    message.get("sources", [])
                )


def show_welcome_message(role: str) -> None:
    if st.session_state.messages:
        return

    st.info(
        f"You are currently using the assistant as **{role}**. "
        "Ask a question about company documents available to your role."
    )