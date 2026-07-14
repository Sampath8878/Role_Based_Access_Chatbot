from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings


@lru_cache(maxsize=1)
def get_embeddings():

    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "huggingface":

        return HuggingFaceEmbeddings(

            model_name=settings.EMBEDDING_MODEL,

            model_kwargs={
                "device": "cpu"
            },

            encode_kwargs={
                "normalize_embeddings": True
            }

        )

    raise ValueError(
        f"Unsupported embedding provider: {provider}"
    )