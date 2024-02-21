from langchain_openai import OpenAIEmbeddings as _OpenAIEmbeddings
from pyrag.embeddings.creator import EmbeddingsCreator

openai_embedding_model_names = ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002']


class OpenAIEmbeddings(EmbeddingsCreator):
    def __init__(self, model_name: str = openai_embedding_model_names[0]):
        super().__init__(_OpenAIEmbeddings(model=model_name).embed_documents)
