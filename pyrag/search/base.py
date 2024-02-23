from abc import ABC, abstractmethod
from typing import Optional
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.typing import SearchInput, SearchResult


class BaseSearch(ABC):
    def __init__(self, db: Database, embeddings: Embeddings):
        self.db = db
        self.embeddings = embeddings

    @abstractmethod
    def __call__(
        self,
        table_name: str,
        input: SearchInput,
        limit: Optional[int] = None,
    ) -> SearchResult:
        pass
