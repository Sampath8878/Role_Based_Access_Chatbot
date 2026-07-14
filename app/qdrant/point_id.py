import hashlib
import uuid


class PointIDGenerator:

    @staticmethod
    def generate(chunk):

        document_id = chunk.metadata["document_id"]

        chunk_index = chunk.metadata["chunk_index"]

        text = chunk.page_content

        unique_name = f"{document_id}_{chunk_index}_{text}"

        hash_hex = hashlib.md5(
            unique_name.encode("utf-8")
        ).hexdigest()

        # Qdrant point IDs must be an unsigned integer or a valid UUID
        # string. Reshape the 32-char MD5 hex digest into UUID form
        # (8-4-4-4-12) so the same input always produces the same,
        # Qdrant-valid ID.
        formatted_uuid = (
            f"{hash_hex[0:8]}-{hash_hex[8:12]}-"
            f"{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
        )

        return formatted_uuid