from typing import List
from numpy import array
from langchain_community.embeddings import HuggingFaceEmbeddings


def create_factory():
    model = HuggingFaceEmbeddings()

    def create(input: str | List[str]):
        input_list: List[str]

        if isinstance(input, list):
            input_list = input
        elif isinstance(input, str):
            input_list = [input]
        else:
            raise ValueError('Input must have the type of str or List[str]')

        return [array(i, dtype='<f4') for i in model.embed_documents(input_list)]

    return create
