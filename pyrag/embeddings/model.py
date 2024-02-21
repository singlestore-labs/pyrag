from typing import Optional
from pyrag.embeddings.creator import EmbeddingsCreator
from pyrag.embeddings.huggingface import HuggingFaceEmbeddingsCreator
from pyrag.embeddings.openai import OpenAIEmbeddingsCreator, openai_embedding_model_names
from pyrag.embeddings.typing import Embedder, EmbeddingModelName


class EmbeddingsModel:
    def __init__(self, model_name: Optional[EmbeddingModelName] = None, embedder: Optional[Embedder] = None):
        if embedder:
            self.embed = EmbeddingsCreator(embedder)
        elif model_name in openai_embedding_model_names:
            self.embed = OpenAIEmbeddingsCreator(model_name)
        else:
            self.embed = HuggingFaceEmbeddingsCreator()
