from typing import Callable

EmbeddingModelName = str
EmbeddingInput = str | list[str]
Embedding = list[float]
Embeddings = list[Embedding]

EmbedderInput = list[str]
Embedder = Callable[[EmbedderInput], Embeddings]
