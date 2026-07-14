import hashlib
from pathlib import Path


class FileHasher:

    @staticmethod
    def sha256(file_path: str) -> str:
        hash_object = hashlib.sha256()

        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_object.update(chunk)

        return hash_object.hexdigest()

    @staticmethod
    def file_size(file_path: str) -> int:
        return Path(file_path).stat().st_size