from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings


class FilesManager:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings
    ):
        self._db = db
        self._embeddings = embeddings
