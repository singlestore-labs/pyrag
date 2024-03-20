from datetime import datetime, timezone
from re import sub
from pandas import read_csv, read_json, DataFrame
from PyPDF2 import PdfReader

from pyrag import helpers


class File:
    def __init__(self, name: str, extension: str, content: str) -> None:
        self.name = name
        self.extension = extension
        self.content = content

    @staticmethod
    def get_extension(name: str) -> str:
        parts = name.split('.')
        return parts[-1] if len(parts) > 1 else ''

    @staticmethod
    def serialize_name(name: str) -> str:
        return sub(r'\W', '_', name)

    def content_to_df(self) -> DataFrame:
        df: DataFrame

        if self.extension == 'csv':
            df = read_csv(self.content)
        elif self.extension == 'json':
            df = read_json(self.content)
        elif self.extension == 'pdf':
            text = ''
            reader = PdfReader(self.content)
            for page in reader.pages:
                text += page.extract_text()
            df = DataFrame(helpers.text.split_recursively(text), columns=['text'])
        elif self.extension == 'txt':
            df = DataFrame(helpers.text.split_recursively(self.content), columns=['text'])
        else:
            raise ValueError('Unsupported file format')

        df['created_at'] = datetime.now().astimezone(timezone.utc)

        return df
