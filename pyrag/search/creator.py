from abc import ABC, abstractmethod
from typing import Optional
from pyrag.db.typing import DBConnection
from pyrag.embeddings.model import EmbeddingsModel
from pyrag.search.typing import SearchInput, SearchResult


class SearchCreator(ABC):
    def __init__(self, db_connection: DBConnection, embeddings_model: EmbeddingsModel):
        self.db_connection = db_connection
        self.embeddings_model = embeddings_model

    @abstractmethod
    def __call__(
        self,
        table_name: str,
        input: SearchInput,
        limit: Optional[int] = None,
        *args,
        **kwargs
    ) -> SearchResult:
        pass
