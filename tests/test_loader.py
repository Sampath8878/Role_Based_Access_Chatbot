import logging

from app.ingestion.document_loader import UniversalDocumentLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

loader = UniversalDocumentLoader("documents")

documents = loader.load_documents()

print("=" * 70)

print(f"Loaded Documents : {len(documents)}")

print("=" * 70)

for document in documents[:3]:

    print(document.metadata)

    print()

    print(document.page_content[:300])

    print("=" * 70)