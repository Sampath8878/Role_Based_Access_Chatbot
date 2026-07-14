from qdrant_client.models import Filter
from qdrant_client.models import FieldCondition
from qdrant_client.models import MatchValue


class DuplicateChecker:

    def __init__(self, client, collection):

        self.client = client

        self.collection = collection

    def exists(self, file_hash):

        result = self.client.scroll(

            collection_name=self.collection,

            scroll_filter=Filter(

                must=[

                    FieldCondition(

                        key="file_hash",

                        match=MatchValue(

                            value=file_hash

                        )

                    )

                ]

            ),

            limit=1

        )

        points = result[0]

        return len(points) > 0