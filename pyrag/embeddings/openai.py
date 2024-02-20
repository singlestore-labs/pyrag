from typing import List, Optional
from numpy import array
from langchain_openai import OpenAIEmbeddings

models = ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002']


def create_factory(model_name: Optional[str] = models[0]):
    if not model_name:
        raise ValueError('model_name is required')

    model = OpenAIEmbeddings(model=model_name)

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
