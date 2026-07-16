from app.ingestion.document_loader import UniversalDocumentLoader

from app.chunking.splitter import DocumentSplitter

from app.qdrant.payload_builder import PayloadBuilder


loader = UniversalDocumentLoader("documents")

documents = loader.load_documents()

splitter = DocumentSplitter()

chunks = splitter.split_documents(documents)

payload = PayloadBuilder.build(chunks[0])

print("=" * 60)

for key, value in payload.items():

    print(f"{key}: {value}")