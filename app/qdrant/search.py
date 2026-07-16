from app.ai.embedding_factory import get_embeddings

from app.qdrant.filters import RoleFilter

from app.qdrant.manager import QdrantManager


class QdrantSearcher:

    def __init__(self):

        self.manager = QdrantManager()

        self.client = self.manager.client

        self.collection = self.manager.collection

        self.embedding = get_embeddings()

    def search(

        self,

        question,

        role,

        limit=5

    ):

        vector = self.embedding.embed_query(

            question

        )

        search_filter = RoleFilter.build(

            role

        )

        results = self.client.query_points(

            collection_name=self.collection,

            query=vector,

            query_filter=search_filter,

            limit=limit,

            with_payload=True

        )

        return results.points