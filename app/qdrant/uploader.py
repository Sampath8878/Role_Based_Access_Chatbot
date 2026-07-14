from qdrant_client.models import PointStruct

from app.ai.embedding_factory import get_embeddings
from app.qdrant.payload_builder import PayloadBuilder
from app.qdrant.point_id import PointIDGenerator
from app.qdrant.duplicate_checker import DuplicateChecker

BATCH_SIZE = 50


class QdrantUploader:

    def __init__(self, manager):

        self.manager = manager
        self.client = manager.client
        self.collection = manager.collection
        self.embedding_model = get_embeddings()

        self.duplicate_checker = DuplicateChecker(
            self.client,
            self.collection
        )

    def upload(self, chunks):

        points = []

        uploaded_chunks = 0
        skipped_chunks = 0

        uploaded_documents = 0
        skipped_documents = 0

        processed_files = {}

        for chunk in chunks:

            payload = PayloadBuilder.build(chunk)

            file_hash = payload["file_hash"]

            # ---------------------------------------
            # Check duplicate ONLY once per document
            # ---------------------------------------
            if file_hash not in processed_files:

                already_exists = self.duplicate_checker.exists(file_hash)

                processed_files[file_hash] = already_exists

                if already_exists:
                    skipped_documents += 1
                    skipped_chunks += 1
                    continue

                uploaded_documents += 1

            else:

                # Entire document already exists
                if processed_files[file_hash]:
                    skipped_chunks += 1
                    continue

            vector = self.embedding_model.embed_query(
                chunk.page_content
            )

            point = PointStruct(
                id=PointIDGenerator.generate(chunk),
                vector=vector,
                payload={
                    **payload,
                    "text": chunk.page_content,
                    "text_length": len(chunk.page_content)
                }
            )

            points.append(point)

            uploaded_chunks += 1

            if len(points) >= BATCH_SIZE:
                self._upsert_batch(points)
                points = []

        if points:
            self._upsert_batch(points)

        print()
        print("=" * 60)
        print("Upload Summary")
        print("=" * 60)
        print(f"Uploaded Documents : {uploaded_documents}")
        print(f"Skipped Documents  : {skipped_documents}")
        print(f"Uploaded Chunks    : {uploaded_chunks}")
        print(f"Skipped Chunks     : {skipped_chunks}")
        print("=" * 60)

    def _upsert_batch(self, points):

        self.client.upsert(
            collection_name=self.collection,
            wait=True,
            points=points
        )

        print(f"Upserted {len(points)} chunks")