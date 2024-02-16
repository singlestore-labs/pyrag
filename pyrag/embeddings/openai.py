from typing import List
from langchain_openai import OpenAIEmbeddings

models = ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002']


def create_factory(model_name=models[0]):
    model = OpenAIEmbeddings(model=model_name)

    def create(input: str | List[str]):
        input_list: List[str]

        if isinstance(input, list):
            input_list = input
        elif isinstance(input, str):
            input_list = [input]
        else:
            raise ValueError('Input must have the type of str or List[str]')

        return model.embed_documents(input_list)

    return create
