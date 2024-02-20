from typing import Any, Callable, List, Optional
from numpy.typing import NDArray

from . import openai
from . import huggingface

EmbeddingModelName = Optional[str]
EmbeddingInput = str | List[str]
CreateEmbeddings = Callable[[str | List[str]], List[NDArray[Any]]]


def create_factory(model_name: EmbeddingModelName) -> CreateEmbeddings:
    if model_name in openai.models:
        return openai.create_factory(model_name)

    return huggingface.create_factory()
