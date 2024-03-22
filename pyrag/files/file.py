from datetime import UTC, datetime
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
    ):
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

    def content_to_df(
        self,
        content_column_name: str = 'content',
        chunk_size: int = 1024,
        chunk_overlap: int = 128
    ) -> DataFrame:
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
            df = DataFrame(
                helpers.text.split_recursively(text, chunk_size, chunk_overlap), columns=[content_column_name]
            )
        elif self.extension == 'txt' and type(self.content) == str:
            df = DataFrame(
                helpers.text.split_recursively(self.content, chunk_size, chunk_overlap), columns=[content_column_name]
            )
        else:
            raise ValueError('Unsupported file format')

        df['updated_at'] = self.updated_at

        return df
