from abc import ABC, abstractmethod

from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.files.file import File


class BaseFilesSource(ABC):
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings
    ):
        super().__init__()
        self._db = db
        self._embeddings = embeddings

    @abstractmethod
    def get_files(self) -> list[File]:
        pass
