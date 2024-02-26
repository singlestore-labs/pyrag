from abc import ABC

from pyrag.embeddings.typing import Embed, EmbedInput, EmbeddingsInput, Embedding


class BaseEmbeddings(ABC):
    def __init__(self, embed: Embed):
        super().__init__()
        self.embed = embed

    def _sanitize_input(self, input: EmbeddingsInput) -> EmbedInput:
        if isinstance(input, list):
            return input

        if isinstance(input, str):
            return [input]

        raise ValueError('Input must have the type of str or list[str]')

    def create(self, input: EmbeddingsInput) -> list[Embedding]:
        return self.embed(self._sanitize_input(input))
