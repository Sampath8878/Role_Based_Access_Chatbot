from app.config.settings import settings
from app.qdrant.client import QdrantConnection

print("=" * 60)
print("QDRANT_URL :", settings.QDRANT_URL)
print("COLLECTION :", settings.QDRANT_COLLECTION)
print("=" * 60)

client = QdrantConnection.get_client()

collections = client.get_collections()

print(collections)