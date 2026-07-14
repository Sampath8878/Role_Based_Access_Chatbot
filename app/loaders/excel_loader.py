import pandas as pd

from langchain_core.documents import Document


def load_excel(path):

    df = pd.read_excel(path)

    docs = []

    for _, row in df.iterrows():

        text = "\n".join(
            f"{column}: {row[column]}"
            for column in df.columns
        )

        docs.append(
            Document(
                page_content=text
            )
        )

    return docs