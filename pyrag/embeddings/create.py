from .typing import CreateEmbeddings, EmbeddingModelName
from . import openai
from . import huggingface


def create_factory(model_name: EmbeddingModelName) -> CreateEmbeddings:
    if model_name in openai.models:
        return openai.create_factory(model_name)

    return huggingface.create_factory()
