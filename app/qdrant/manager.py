from qdrant_client.models import Distance
from qdrant_client.models import PayloadSchemaType
from qdrant_client.models import VectorParams

from app.config.settings import settings
from app.qdrant.client import QdrantConnection


class QdrantManager:

    # Payload fields that get filtered on (duplicate checks, RBAC search)
    # and therefore need a Qdrant payload index or filtering returns 400.
    KEYWORD_INDEX_FIELDS = [
        "file_hash",
        "allowed_roles",
        "department",
    ]

    def __init__(self):
        self.client = QdrantConnection.get_client()
        self.collection = settings.QDRANT_COLLECTION
        self.vector_size = settings.VECTOR_SIZE

    def collection_exists(self):
        collections = self.client.get_collections()
        names = [collection.name for collection in collections.collections]
        return self.collection in names

    def create_collection(self):
        if self.collection_exists():
            print(f"Collection '{self.collection}' already exists.")
            self.create_indexes()
            return

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE
            )
        )

        print(f"Collection '{self.collection}' created successfully.")

        self.create_indexes()

    def create_indexes(self):
        for field_name in self.KEYWORD_INDEX_FIELDS:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection,
                    field_name=field_name,
                    field_schema=PayloadSchemaType.KEYWORD
                )
                print(f"Index ensured for '{field_name}'.")
            except Exception as e:
                print(f"Index skipped for '{field_name}': {e}")

    def delete_collection(self):
        if self.collection_exists():
            self.client.delete_collection(self.collection)
            print(f"Collection '{self.collection}' deleted.")
        else:
            print("Collection not found.")

    def collection_info(self):
        if not self.collection_exists():
            print("Collection not found.")
            return

        info = self.client.get_collection(self.collection)
        print(info)