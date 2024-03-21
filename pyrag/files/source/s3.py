from datetime import datetime
from io import BytesIO, StringIO
import boto3
from os import environ
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
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket_name)
            files = response.get('Contents')
            return [] if not files else files
        except Exception as e:
            print(e)
            return []

    def _get_file_content(self, key: str):
        try:
            obj = self.client.get_object(Bucket=self.bucket_name, Key=key)
            content = obj['Body'].read()
            extension = File.get_extension(key)

            if extension == 'csv' or extension == 'json':
                content = StringIO(content.decode('utf-8'))
            elif extension == 'pdf':
                content = BytesIO(content)
            else:
                content = content.decode('utf-8')

            return content
        except Exception as e:
            print(e)
            return ''

    def get_files(self) -> list[File]:
        files: list[File] = []

        for file in self._get_files():
            name = file['Key']
            content = self._get_file_content(name)
            updated_at = int(datetime.timestamp(file['LastModified']))
            files.append(File(name, content, updated_at=updated_at))

        return files
