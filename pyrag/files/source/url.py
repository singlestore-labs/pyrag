from io import BytesIO, StringIO
from typing import Optional
import requests

from pyrag.files.file import File
from pyrag.files.source.base import BaseFilesSource


class URLFilesSource(BaseFilesSource):
    def sync_file(
        self,
        url: str,
        name: Optional[str] = None,
        content_column_name: Optional[str] = None,
        vector_column_name: Optional[str] = None,
        content_chunk_size: int = 1024,
        content_chunk_overlap: int = 128
    ):
        if not name:
            parts = url.split('/')
            name = parts[-1] if len(parts) > 1 else ''

        response = requests.get(url)

        if response.status_code == 200:
            extension = File.get_extension(name)

            if extension == 'csv' or extension == 'json':
                content = StringIO(response.content.decode('utf-8'))
            elif extension == 'pdf':
                content = BytesIO(response.content)
            else:
                content = response.content.decode('utf-8')

            file = File(name, content)
            self._sync_file(
                file=file,
                content_column_name=content_column_name,
                vector_column_name=vector_column_name,
                ignore_is_updated=True,
                content_chunk_size=content_chunk_size,
                content_chunk_overlap=content_chunk_overlap
            )
        else:
            print(f'Failed to fetch the file: {url}', f'\nStatus code: {response.status_code}')
