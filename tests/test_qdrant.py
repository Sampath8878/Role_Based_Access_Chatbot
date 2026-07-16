from app.qdrant.manager import QdrantManager

manager = QdrantManager()

manager.create_collection()

manager.collection_info()