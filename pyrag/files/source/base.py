from json import dumps
from typing import Optional

from pandas import DataFrame

from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.files.file import File


def df_to_chunks(df: DataFrame, chunk_size: int):
    for i in range(0, df.shape[0], chunk_size):
        yield df[i:i + chunk_size].copy()


class BaseFilesSource:
    def __init__(self, db: Database, embeddings: Embeddings):
        self._db = db
        self._embeddings = embeddings

    def _create_file_table(self, table_name: str, content_column_name: str, vector_column_name: str):
        self._db.create_table(table_name, [
            ('id', 'BIGINT AUTO_INCREMENT PRIMARY KEY'),
            ('_index', 'BIGINT'),
            ('updated_at', 'INT'),
            (content_column_name, 'LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci'),
            (vector_column_name, f'VECTOR({self._embeddings.dimension}) NOT NULL'),
        ])

        with self._db.cursor() as cursor:
            cursor.execute(f'''
                ALTER TABLE {table_name} ADD VECTOR INDEX vector_index ({vector_column_name})
                INDEX_OPTIONS '{{"index_type": "IVF_PQ", "nlist": 4000}}'
            ''')

            cursor.fetchall()

    def _insert_file(
        self,
        file: File,
        table_name: str,
        content_column_name: str,
        vector_column_name: str,
        content_chunk_size: int = 1024,
        content_chunk_overlap: int = 128
    ):
        index = 0
        df = file.content_to_df(content_column_name, chunk_size=content_chunk_size, chunk_overlap=content_chunk_overlap)

        def process_records(df: DataFrame):
            values = []
            records = [dumps(i) for i in df.to_dict('records')]
            df['embedding'] = [str(i) for i in self._embeddings.create(records)]

            for i, row in df.iterrows():
                nonlocal index
                embedding = row.pop('embedding')
                content = row.to_json()
                values.append((index, row['updated_at'], content, embedding))
                index += 1

            with self._db.cursor() as cursor:
                cursor.executemany(f'''
                    INSERT INTO {table_name} (_index, updated_at, {content_column_name}, {vector_column_name})
                    VALUES (%s, %s, %s, %s)
                ''', values)
                cursor.fetchall()

        if len(df) > 500:
            for df_chunk in df_to_chunks(df, 500):
                process_records(df_chunk)
        else:
            process_records(df)

    def _is_file_updated(self, table_name: str, updated_at: int):
        try:
            with self._db.cursor() as cursor:
                cursor.execute(f'SELECT updated_at FROM {table_name} LIMIT 1')
                result = cursor.fetchone()
                if type(result) != tuple:
                    return False
                return result[0] >= updated_at
        except:
            return False

    def _sync_file(
        self,
        file: File,
        table_name: Optional[str] = None,
        content_column_name: Optional[str] = None,
        vector_column_name: Optional[str] = None,
        ignore_is_updated: Optional[bool] = False,
        content_chunk_size: int = 1024,
        content_chunk_overlap: int = 128
    ):
        content_column_name = content_column_name or 'content'
        vector_column_name = vector_column_name or 'v'
        _table_name = table_name or File.serialize_name(file.name)
        is_exists = self._db.is_table_exists(_table_name)
        is_updated = True if ignore_is_updated else self._is_file_updated(_table_name, file.updated_at)

        if is_exists and is_updated:
            return

        self._db.drop_table(_table_name)
        self._create_file_table(_table_name, content_column_name, vector_column_name)
        self._insert_file(
            file=file,
            table_name=_table_name,
            content_column_name=content_column_name,
            vector_column_name=vector_column_name,
            content_chunk_size=content_chunk_size,
            content_chunk_overlap=content_chunk_overlap
        )

    def _sync_files(
        self,
        files: list[File],
        table_names: dict = {},
        content_column_name: Optional[str] = None,
        vector_column_name: Optional[str] = None,
        ignore_is_updated: Optional[bool] = False,
        content_chunk_size: int = 1024,
        content_chunk_overlap: int = 128
    ):
        for file in files:
            self._sync_file(
                file=file,
                table_name=table_names[file.name],
                content_column_name=content_column_name,
                vector_column_name=vector_column_name,
                ignore_is_updated=ignore_is_updated,
                content_chunk_size=content_chunk_size,
                content_chunk_overlap=content_chunk_overlap
            )
