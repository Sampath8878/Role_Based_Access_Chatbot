from pathlib import Path

from app.utils.hash_utils import FileHasher


class PayloadBuilder:

    @staticmethod
    def normalize_role(role):
        return (
            role.lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

    @staticmethod
    def build(chunk):
        metadata = chunk.metadata.copy()

        metadata["allowed_roles"] = [
            PayloadBuilder.normalize_role(role)
            for role in metadata.get("allowed_roles", [])
        ]

        metadata["role_count"] = len(metadata["allowed_roles"])

        metadata["department"] = metadata["department"].lower()
        metadata["owner"] = metadata["owner"].lower()
        metadata["document_type"] = metadata["document_type"].lower()
        metadata["security_level"] = metadata["security_level"].lower()

        source = Path(metadata["source"]).resolve()

        if source.exists():
            metadata["file_hash"] = FileHasher.sha256(str(source))
            metadata["file_size"] = FileHasher.file_size(str(source))
        else:
            print(f"WARNING: File not found -> {source}")
            metadata["file_hash"] = ""
            metadata["file_size"] = 0

        return metadata