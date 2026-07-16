from app.rag.retriever import Retriever


retriever = Retriever()

while True:

    print()

    role = input(

        "Role : "

    ).strip().lower()

    question = input(

        "Question : "

    )

    print()

    results = retriever.retrieve(

        question,

        role,

        top_k=5

    )

    if len(results) == 0:

        print("No Documents Found")

        continue

    print("=" * 80)

    for i, result in enumerate(results, start=1):

        print()

        print(f"Result {i}")

        print("-" * 80)

        print(

            "Score :",

            round(result["score"], 4)

        )

        print(

            "Department :",

            result["department"]

        )

        print(

            "Document :",

            result["file_name"]

        )

        print()

        print(result["text"][:700])

        print()

        print("=" * 80)