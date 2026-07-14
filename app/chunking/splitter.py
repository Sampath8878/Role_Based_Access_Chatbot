import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentSplitter:

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(

            chunk_size=800,

            chunk_overlap=100

        )

    def split_documents(self, documents):

        all_chunks = []

        for document in documents:

            chunks = self.splitter.split_documents([document])

            document_hash = document.metadata["file_hash"]

            chunk_count = len(chunks)

            for index, chunk in enumerate(chunks):

                chunk.metadata["document_id"] = document_hash

                chunk.metadata["chunk_index"] = index

                chunk.metadata["chunk_count"] = chunk_count

                chunk.metadata["chunk_id"] = (

                    f"{document_hash}_{index}"

                )

            all_chunks.extend(chunks)

        return all_chunks