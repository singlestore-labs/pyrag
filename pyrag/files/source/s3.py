from io import BytesIO, StringIO
from typing import Optional
import boto3
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.files.file import File
from pyrag.files.source.base import BaseFilesSource


class S3FilesSource(BaseFilesSource):
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
    ):
        super().__init__(db, embeddings)
        self.bucket_name = bucket_name
        self.client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

    def _get_files(self):
        response = self.client.list_objects_v2(Bucket=self.bucket_name)
        files = response.get('Contents')
        return [] if not files else files

    def _get_file_content(self, key: str):
        obj = self.client.get_object(Bucket=self.bucket_name, Key=key)
        content = obj['Body'].read()
        extension = File.get_extension(key)

        if extension == 'csv' or extension == 'json':
            return StringIO(content.decode('utf-8'))
        elif extension == 'pdf':
            return BytesIO(content)
        else:
            return content.decode('utf-8')

    def sync_files(
        self,
        table_names: dict = {},
        allowed_files: list[str] = [],
        ignored_files: list[str] = [],
        min_updated_at: Optional[int] = None,
        content_column_name: Optional[str] = 'content',
        vector_column_name: Optional[str] = 'v',
        ignore_is_updated: Optional[bool] = False,
        content_chunk_size: int = 1024,
        content_chunk_overlap: int = 128
    ):
        files: list[File] = []

        for file in self._get_files():
            name = file['Key']
            updated_at = int(file['LastModified'].timestamp())

            if len(allowed_files) and not name in allowed_files:
                continue

            if name in ignored_files or (min_updated_at and updated_at < min_updated_at):
                continue

            content = self._get_file_content(name)
            files.append(File(name, content, updated_at=updated_at))

        self._sync_files(
            files=files,
            table_names=table_names,
            content_column_name=content_column_name,
            vector_column_name=vector_column_name,
            ignore_is_updated=ignore_is_updated,
            content_chunk_size=content_chunk_size,
            content_chunk_overlap=content_chunk_overlap
        )
