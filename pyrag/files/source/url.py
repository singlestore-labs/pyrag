from io import BytesIO, StringIO
from typing import Optional
import requests

from pyrag.files.file import File
from pyrag.files.source.base import BaseFilesSource


class URLFilesSource(BaseFilesSource):
    def sync_file(self, url: str, name: Optional[str] = None, content_chunk_size: int = 1024):
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
            self._sync_file(file, ignore_is_updated=True, content_chunk_size=content_chunk_size)
        else:
            print(f'Failed to fetch the file: {url}', f'\nStatus code: {response.status_code}')
