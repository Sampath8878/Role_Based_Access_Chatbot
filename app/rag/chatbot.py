from typing import Any, Dict, List

from app.auth.roles import RoleManager
from app.llm.groq_client import GroqClient
from app.rag.memory import ConversationMemory
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever
from app.security.guardrails import SecurityGuardrail
from app.tools.structured_data import StructuredDataService


class FinSolveChatbot:
    def __init__(self) -> None:
        self.retriever = Retriever()

        self.llm = GroqClient()

        self.memory = ConversationMemory(
            max_history=3
        )

        self.structured_data = (
            StructuredDataService()
        )

        self.security_guardrail = (
            SecurityGuardrail()
        )

    @staticmethod
    def validate_question(
        question: str,
    ) -> str:
        if question is None:
            raise ValueError(
                "Question cannot be empty."
            )

        cleaned_question = question.strip()

        if not cleaned_question:
            raise ValueError(
                "Question cannot be empty."
            )

        if len(cleaned_question) > 2000:
            raise ValueError(
                "Question is too long. "
                "Maximum length is 2000 characters."
            )

        return cleaned_question

    @staticmethod
    def clean_answer(
        answer: str,
    ) -> str:
        if not answer:
            return (
                "I could not generate an answer."
            )

        paragraphs = [
            paragraph.strip()
            for paragraph in answer.split(
                "\n\n"
            )
            if paragraph.strip()
        ]

        unique_paragraphs = []

        seen_paragraphs = set()

        for paragraph in paragraphs:
            paragraph_key = (
                paragraph.lower()
                .strip()
            )

            if paragraph_key in seen_paragraphs:
                continue

            seen_paragraphs.add(
                paragraph_key
            )

            unique_paragraphs.append(
                paragraph
            )

        return "\n\n".join(
            unique_paragraphs
        ).strip()

    @staticmethod
    def build_sources(
        documents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        sources = []

        seen_sources = set()

        for document in documents:
            metadata = document.get(
                "metadata",
                {},
            )

            file_name = document.get(
                "file_name",
                metadata.get(
                    "file_name",
                    "Unknown document",
                ),
            )

            department = document.get(
                "department",
                metadata.get(
                    "department",
                    "Unknown department",
                ),
            )

            chunk_index = metadata.get(
                "chunk_index"
            )

            source_key = (
                file_name,
                chunk_index,
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(
                source_key
            )

            sources.append(
                {
                    "file": file_name,
                    "department": department,
                    "chunk_index": chunk_index,
                    "score": document.get(
                        "score"
                    ),
                    "source_type": "qdrant",
                }
            )

        return sources

    def save_memory(
        self,
        session_id: str,
        question: str,
        answer: str,
    ) -> None:
        self.memory.add(
            session_id=session_id,
            question=question,
            answer=answer,
        )

    def chat(
        self,
        role: str,
        question: str,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        try:
            normalized_role = (
                RoleManager.normalize_role(
                    role
                )
            )

        except ValueError as error:
            return {
                "answer": str(error),
                "sources": [],
                "authorized": False,
                "response_type": (
                    "validation_error"
                ),
            }

        if not RoleManager.is_valid_internal_role(
            normalized_role
        ):
            return {
                "answer": (
                    "The selected user role "
                    "is invalid."
                ),
                "sources": [],
                "authorized": False,
                "response_type": (
                    "validation_error"
                ),
            }

        try:
            cleaned_question = (
                self.validate_question(
                    question
                )
            )

        except ValueError as error:
            return {
                "answer": str(error),
                "sources": [],
                "authorized": False,
                "response_type": (
                    "validation_error"
                ),
            }

        # Security must run before CSV analysis,
        # Qdrant retrieval and Groq.
        guardrail_result = (
            self.security_guardrail.validate(
                role=normalized_role,
                question=cleaned_question,
            )
        )

        if not guardrail_result.allowed:
            answer = (
                guardrail_result.message
                or "Access denied."
            )

            self.save_memory(
                session_id=session_id,
                question=cleaned_question,
                answer=answer,
            )

            return {
                "answer": answer,
                "sources": [],
                "authorized": False,
                "response_type": (
                    guardrail_result.reason
                    or "access_denied"
                ),
            }

        # Exact HR aggregation uses all CSV rows.
        structured_result = (
            self.structured_data.answer(
                role=normalized_role,
                question=cleaned_question,
            )
        )

        if structured_result is not None:
            structured_result["answer"] = (
                self.clean_answer(
                    structured_result["answer"]
                )
            )

            self.save_memory(
                session_id=session_id,
                question=cleaned_question,
                answer=structured_result[
                    "answer"
                ],
            )

            return structured_result

        documents = self.retriever.retrieve(
            question=cleaned_question,
            role=normalized_role,
            top_k=5,
        )

        if not documents:
            answer = (
                "I could not find that information "
                "in the documents available to "
                "your role."
            )

            self.save_memory(
                session_id=session_id,
                question=cleaned_question,
                answer=answer,
            )

            return {
                "answer": answer,
                "sources": [],
                "authorized": True,
                "response_type": (
                    "rag_no_results"
                ),
            }

        history = self.memory.get(
            session_id
        )

        prompt = PromptBuilder.build(
            role=normalized_role,
            question=cleaned_question,
            documents=documents,
            history=history,
        )

        try:
            generated_answer = (
                self.llm.generate(
                    prompt
                )
            )

            answer = self.clean_answer(
                generated_answer
            )

        except Exception as error:
            error_text = str(
                error
            ).lower()

            if (
                "429" in error_text
                or "rate_limit" in error_text
            ):
                answer = (
                    "The AI service has temporarily "
                    "reached its usage limit. "
                    "Please try again shortly."
                )
            else:
                answer = (
                    "The AI service could not "
                    "generate a response at this time."
                )

            return {
                "answer": answer,
                "sources": self.build_sources(
                    documents
                ),
                "authorized": True,
                "response_type": "llm_error",
            }

        self.save_memory(
            session_id=session_id,
            question=cleaned_question,
            answer=answer,
        )

        return {
            "answer": answer,
            "sources": self.build_sources(
                documents
            ),
            "authorized": True,
            "response_type": "rag",
        }

    def clear_memory(
        self,
        session_id: str = "default",
    ) -> None:
        self.memory.clear(
            session_id
        )