import pandas as pd

from langchain_core.documents import Document


def load_csv(path):

    df = pd.read_csv(path)

    documents = []

    for _, row in df.iterrows():

        text = "\n".join(
            f"{column}: {row[column]}"
            for column in df.columns
        )

        documents.append(
            Document(
                page_content=text
            )
        )

    return documents