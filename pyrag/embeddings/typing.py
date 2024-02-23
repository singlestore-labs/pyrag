from typing import Callable


Embedding = list[float]
EmbeddingsInput = list[str] | str
EmbedInput = list[str]
Embed = Callable[[EmbedInput], list[Embedding]]
