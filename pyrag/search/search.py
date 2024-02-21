from typing import Optional
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch


class Search():
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        search_name: Optional[str] = None
    ):
        if search_name == 'semantic':
            self.search = SemanticSearch(db, embeddings)

        if not self.search:
            raise ValueError('Unsupported search')
