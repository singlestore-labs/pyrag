from typing import Callable, List

EmbeddingModelName = str
EmbeddingInput = str | List[str]
Embedding = List[float]
Embeddings = List[Embedding]

EmbedderInput = List[str]
Embedder = Callable[[EmbedderInput], Embeddings]
