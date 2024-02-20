from typing import Callable, List, Optional

EmbeddingModelName = Optional[str]
EmbeddingInput = str | List[str]
CreateEmbeddings = Callable[[str | List[str]], List[List[float]]]
