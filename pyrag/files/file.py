from datetime import UTC, datetime, timezone
from io import BytesIO, StringIO
from re import sub
from typing import Optional
from pandas import read_csv, read_json, DataFrame
from PyPDF2 import PdfReader

from pyrag import helpers


class File:
    def __init__(
        self,
        name: str, content: str | StringIO | BytesIO,
        extension: Optional[str] = None,
        updated_at: int = int(datetime.timestamp(datetime.now(UTC)))
    ) -> None:
        self.name = name
        self.extension = extension or self.get_extension(name)
        self.content = content
        self.updated_at = updated_at

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
            df = DataFrame(helpers.text.split(text), columns=['text'])
        elif self.extension == 'txt' and type(self.content) == str:
            df = DataFrame(helpers.text.split(self.content), columns=['text'])
        else:
            raise ValueError('Unsupported file format')

        df['updated_at'] = self.updated_at

        return df
