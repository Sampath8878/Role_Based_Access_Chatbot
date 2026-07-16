from app.qdrant.manager import QdrantManager


def main():

    manager = QdrantManager()

    if manager.collection_exists():

        print("Current collection config:")
        manager.collection_info()

        print()
        print(f"Deleting collection '{manager.collection}'...")
        manager.delete_collection()

    print()
    print("Recreating collection with correct (unnamed) vector config...")
    manager.create_collection()

    print()
    print("Done. You can now rerun ingest_pipeline.py")


if __name__ == "__main__":
    main()