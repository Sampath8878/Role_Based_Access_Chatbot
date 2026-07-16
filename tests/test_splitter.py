from app.ingestion.document_loader import UniversalDocumentLoader
from app.chunking.splitter import DocumentSplitter

loader = UniversalDocumentLoader("documents")

documents = loader.load_documents()

splitter = DocumentSplitter()

chunks = splitter.split_documents(documents)

print(f"Documents : {len(documents)}")

print(f"Chunks : {len(chunks)}")

print()

print(chunks[0].metadata)

print()

print(chunks[0].page_content)