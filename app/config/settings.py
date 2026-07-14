from pathlib import Path
import os

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ENV_PATH)


class Settings:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    QDRANT_URL = os.getenv("QDRANT_URL")

    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    QDRANT_COLLECTION = os.getenv(
        "QDRANT_COLLECTION",
        "company_docs"
    )

    EMBEDDING_PROVIDER = os.getenv(
        "EMBEDDING_PROVIDER",
        "huggingface"
    )

    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "BAAI/bge-small-en-v1.5"
    )

    VECTOR_SIZE = int(
        os.getenv(
            "VECTOR_SIZE",
            "384"
        )
    )

    LLM_PROVIDER = os.getenv(
        "LLM_PROVIDER",
        "groq"
    )

    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "llama-3.3-70b-versatile"
    )


settings = Settings()