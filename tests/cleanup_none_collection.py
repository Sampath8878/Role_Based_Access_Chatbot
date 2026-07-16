from qdrant_client import QdrantClient
from app.config.settings import settings

client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)

collections = [c.name for c in client.get_collections().collections]
print("Existing collections:", collections)

if "None" in collections:
    client.delete_collection("None")
    print("Deleted phantom 'None' collection.")
else:
    print("No phantom 'None' collection found.")