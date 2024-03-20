from abc import ABC, abstractmethod

from pyrag.files.file import File


class FilesSourceBase(ABC):
    @abstractmethod
    def get_files(self) -> list[File]:
        pass

    @abstractmethod
    def upload_file(self, file: File):
        pass
