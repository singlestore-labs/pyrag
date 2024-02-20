from typing import Any, Callable, List, Optional
from numpy.typing import NDArray

EmbeddingModelName = Optional[str]
EmbeddingInput = str | List[str]
CreateEmbeddings = Callable[[str | List[str]], List[NDArray[Any]]]
