from abc import ABC, abstractmethod
from typing import Callable, Optional

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
    def get_files(self, is_ignored_file: Callable[[str, int], bool]) -> list[File]:
        pass

    def sync(
        self,
        min_updated_at: Optional[int] = None,
        ignore_file_names: list[str] = []
    ):
        def handle_is_ignored_file(name: str, updated_at: int):
            if name in ignore_file_names or (min_updated_at and updated_at < min_updated_at):
                return True

            return False

        files = self.get_files(handle_is_ignored_file)

        for file in files:
            print(file.name)
