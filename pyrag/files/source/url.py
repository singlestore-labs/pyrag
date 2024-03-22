import requests
from pyrag.files.file import File
from pyrag.files.source.base import BaseFilesSource


class URLFilesSource(BaseFilesSource):
    def _get_file(self, url: str) -> File:
        file = File('', '')

        try:
            response = requests.get(url)
            print(response)
        except Exception as e:
            print(e)

        return file
