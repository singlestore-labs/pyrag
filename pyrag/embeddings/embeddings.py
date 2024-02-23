from typing import Optional

from pyrag.embeddings.openai import openai_embedding_model_names
from pyrag.embeddings.typing import Embed, Embedding, EmbeddingsInput


class Embeddings:
    def __init__(self, model_name: Optional[str] = None, embed: Optional[Embed] = None):
        if embed:
            from pyrag.embeddings.base import BaseEmbeddings
            self.model = BaseEmbeddings(embed)
        elif model_name in openai_embedding_model_names:
            from pyrag.embeddings.openai import OpenAIEmbeddings
            self.model = OpenAIEmbeddings(model_name)
        else:
            from pyrag.embeddings.huggingface import HuggingFaceEmbeddings
            self.model = HuggingFaceEmbeddings()

    def create(self, input: EmbeddingsInput) -> list[Embedding]:
        return self.model.create(input)
