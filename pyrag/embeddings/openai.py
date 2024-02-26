from pyrag.embeddings.base import BaseEmbeddings

openai_embedding_model_names = [
    'text-embedding-3-small',
    'text-embedding-3-large',
    'text-embedding-ada-002'
]


class OpenAIEmbeddings(BaseEmbeddings):
    def __init__(self, model_name: str = openai_embedding_model_names[0]):
        from langchain_openai import OpenAIEmbeddings
        super().__init__(OpenAIEmbeddings(model=model_name).embed_documents)
