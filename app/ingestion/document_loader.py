import logging
import os
from pathlib import Path

from app.config.role_config import ROLE_METADATA
from app.loaders.csv_loader import load_csv
from app.loaders.docx_loader import load_docx
from app.loaders.excel_loader import load_excel
from app.loaders.markdown_loader import load_markdown
from app.loaders.pdf_loader import load_pdf
from app.loaders.text_loader import load_text
from app.utils.hash_utils import FileHasher

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".pdf": load_pdf,
    ".csv": load_csv,
    ".xlsx": load_excel,
    ".docx": load_docx,
    ".txt": load_text,
    ".md": load_markdown
}


class UniversalDocumentLoader:

    def __init__(self, document_root: str):
        self.document_root = document_root

    def load_documents(self):

        all_documents = []

        loaded_files = []
        failed_files = []
        unsupported_files = []

        for department_folder in os.listdir(self.document_root):

            folder_path = os.path.join(self.document_root, department_folder)

            if not os.path.isdir(folder_path):
                continue

            metadata = ROLE_METADATA.get(department_folder.lower())

            if metadata is None:
                logger.warning(f"Unknown department folder: {department_folder}")
                continue

            for root, _, files in os.walk(folder_path):

                for file in files:

                    file_path = os.path.join(root, file)

                    extension = Path(file).suffix.lower()

                    if extension not in SUPPORTED_EXTENSIONS:
                        logger.warning(f"Skipped unsupported file: {file}")
                        unsupported_files.append(file_path)
                        continue

                    try:
                        file_hash = FileHasher.sha256(file_path)
                        file_size = FileHasher.file_size(file_path)
                        loader = SUPPORTED_EXTENSIONS[extension]
                        documents = loader(file_path)

                        for document in documents:
                            document.metadata.update({
                                "department": metadata["department"],
                                "allowed_roles": metadata["allowed_roles"],
                                "security_level": metadata["security_level"],
                                "document_type": metadata["document_type"],
                                "owner": metadata["owner"],
                                "updated": metadata["updated"],
                                "file_name": file,
                                "file_type": extension.replace(".", ""),
                                "source": file_path,
                                "file_hash": file_hash,
                                "file_size": file_size
                            })

                        all_documents.extend(documents)
                        loaded_files.append(file_path)
                        logger.info(f"Loaded {file}")

                    except Exception as e:
                        failed_files.append(file_path)
                        logger.exception(f"Failed loading {file}: {e}")

        logger.info(f"Total loaded documents: {len(all_documents)}")

        print()
        print("=" * 70)
        print("DOCUMENT LOADING REPORT")
        print("=" * 70)

        print(f"Loaded Files      : {len(loaded_files)}")
        print(f"Failed Files      : {len(failed_files)}")
        print(f"Unsupported Files : {len(unsupported_files)}")
        print(f"Documents Loaded  : {len(all_documents)}")

        if failed_files:

            print("\nFAILED FILES")

            for f in failed_files:
                print(f" - {f}")

        if unsupported_files:

            print("\nUNSUPPORTED FILES")

            for f in unsupported_files:
                print(f" - {f}")

        print("=" * 70)

        return all_documents