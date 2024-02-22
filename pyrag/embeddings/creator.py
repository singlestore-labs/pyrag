from pyrag.embeddings.typing import Embedder, EmbedderInput, EmbeddingInput, Embeddings


class EmbeddingsCreator():
    def __init__(self, embedder: Embedder):
        self.embedder = embedder

    def __call__(self, input: EmbeddingInput) -> Embeddings:
        embedder_input: EmbedderInput

        if isinstance(input, list):
            embedder_input = input
        elif isinstance(input, str):
            embedder_input = [input]
        else:
            raise ValueError('Input must have the type of str or list[str]')

        return self.embedder(embedder_input)
