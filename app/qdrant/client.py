from qdrant_client import QdrantClient

from app.config.settings import settings


class QdrantConnection:

    _client = None

    @classmethod
    def get_client(cls):

        if cls._client is None:

            cls._client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY or None,
                timeout=120
            )

        return cls._client