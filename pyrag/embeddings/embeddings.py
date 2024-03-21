from typing import Optional
from os import environ

from pyrag.embeddings.typing import Embed
from pyrag.embeddings.base import BaseEmbeddings


openai_embedding_model_names = [
    'text-embedding-ada-002',
    'text-embedding-3-small',
    'text-embedding-3-large',
]

openai_embedding_model_dimensions = {
    'text-embedding-ada-002': 1536,
    'text-embedding-3-small': 1536,
    'text-embedding-3-large': 3072,
}


class Embeddings:
    def __init__(
        self,
        model_name: Optional[str] = None,
        dimension: Optional[int] = 0,
        embed: Optional[Embed] = None,
    ):
        self.dimension = dimension

        if embed:
            self.model = BaseEmbeddings(embed)
        elif model_name in openai_embedding_model_names:
            from langchain_openai import OpenAIEmbeddings
            from langchain_core.pydantic_v1 import SecretStr
            model_name = model_name or openai_embedding_model_names[0]
            self.dimension = self.dimension or openai_embedding_model_dimensions[model_name] or self.dimension
            self.model = BaseEmbeddings(
                OpenAIEmbeddings(
                    api_key=SecretStr(environ.get('OPENAI_API_KEY', '')),
                    model=model_name,
                ).embed_documents
            )
        else:
            from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
            from langchain_core.pydantic_v1 import SecretStr
            model_name = model_name or 'sentence-transformers/all-MiniLM-L6-v2'
            self.dimension = self.dimension or 384
            self.model = BaseEmbeddings(
                HuggingFaceInferenceAPIEmbeddings(
                    api_key=SecretStr(environ.get('HUGGINGFACEHUB_API_TOKEN', '')),
                    model_name=model_name,
                ).embed_documents
            )

        self.create = self.model.create
        self.dimension = self.dimension or len(self.create('1')[0])
