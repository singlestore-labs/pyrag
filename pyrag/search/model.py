from typing import Optional
from pyrag.db.typing import DBConnection
from pyrag.embeddings.model import EmbeddingsModel
from pyrag.search.semantic import SemanticSearch


class SearchModel():
    def __init__(
        self,
        db_connection: DBConnection,
        embeddings_model: EmbeddingsModel,
        search_name: Optional[str] = None
    ):
        if search_name == 'semantic':
            self.search = SemanticSearch(db_connection, embeddings_model)

        if not self.search:
            raise ValueError('Unsupported search')
