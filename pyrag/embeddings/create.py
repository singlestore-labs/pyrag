from typing import Callable, List, Optional

from . import openai
from . import huggingface

EmbeddingModelName = Optional[str]
CreateEmbeddings = Callable[[str | List[str]], List[List[float]]]


def create_factory(model_name: EmbeddingModelName) -> CreateEmbeddings:
    if model_name in openai.models:
        return openai.create_factory(model_name)

    return huggingface.create_factory()
