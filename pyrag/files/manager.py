from os import environ
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.files.source.s3 import S3FilesSource


class FilesManager:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings
    ):
        self._db = db
        self._embeddings = embeddings

    def s3(
        self,
        access_key_id: str = environ.get('AWS_ACCESS_KEY_ID', ''),
        secret_access_key: str = environ.get('AWS_SECRET_ACCESS_KEY', ''),
        bucket_name: str = environ.get('AWS_BUCKET_NAME', ''),
    ):
        return S3FilesSource(
            db=self._db,
            embeddings=self._embeddings,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            bucket_name=bucket_name,
        )
