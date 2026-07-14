from functools import lru_cache

from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv

import os

load_dotenv()


@lru_cache(maxsize=1)
def get_embedding_model():

    return OpenAIEmbeddings(

        model=os.getenv(
            "EMBEDDING_MODEL",
            "text-embedding-3-small"
        )

    )