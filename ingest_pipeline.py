from app.ingestion.document_loader import UniversalDocumentLoader
from app.chunking.splitter import DocumentSplitter
from app.qdrant.manager import QdrantManager
from app.qdrant.uploader import QdrantUploader


DOCUMENT_PATH = "documents"


def main():
    print()
    print("=" * 60)
    print("Loading Documents...")

    loader = UniversalDocumentLoader(DOCUMENT_PATH)
    documents = loader.load_documents()

    print(f"Loaded {len(documents)} documents")
    print()
    print("=" * 60)
    print("Splitting Documents...")

    splitter = DocumentSplitter()
    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")
    print()
    print("=" * 60)
    print("Connecting Qdrant...")

    manager = QdrantManager()
    manager.create_collection()

    uploader = QdrantUploader(manager)

    print()
    print("=" * 60)
    print("Uploading...")

    uploader.upload(chunks)

    print()
    print("Completed Successfully")


if __name__ == "__main__":
    main()