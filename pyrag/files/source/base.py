from abc import ABC, abstractmethod
from json import dumps
from typing import Callable, Optional

from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.files.file import File


class BaseFilesSource(ABC):
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings
    ):
        super().__init__()
        self._db = db
        self._embeddings = embeddings

    @abstractmethod
    def get_files(self, is_ignored_file: Callable[[str, int], bool]) -> list[File]:
        pass

    def _create_file_table(self, table_name: str, content_column_name: str, vector_column_name: str):
        self._db.create_table(table_name, [
            ('id', 'BIGINT AUTO_INCREMENT PRIMARY KEY'),
            ('_index', 'BIGINT'),
            ('updated_at', 'INT'),
            (content_column_name or 'content', 'LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci'),
            (vector_column_name or 'v', f'VECTOR({self._embeddings.dimension}) NOT NULL'),
        ])

        with self._db.cursor() as cursor:
            cursor.execute(f'''
                ALTER TABLE {table_name} ADD VECTOR INDEX vector_index (v)
                INDEX_OPTIONS '{{"index_type": "IVF_PQ", "nlist": 4000}}'
            ''')

            cursor.fetchall()

    def _is_file_table_synced(self, table_name: str, updated_at: int):
        try:
            with self._db.cursor() as cursor:
                cursor.execute(f'SELECT updated_at FROM {table_name} LIMIT 1')
                result = cursor.fetchone()

                if type(result) != tuple:
                    return False

                return result[0] >= updated_at
        except Exception as e:
            print(e)
            return False

    def _insert_file(self, file: File, table_name: str, content_column_name: str, vector_column_name: str):
        content_column_name = content_column_name or 'content'
        vector_column_name = vector_column_name or 'v'
        df = file.content_to_df(content_column_name)
        records = [dumps(i) for i in df.to_dict('records')]
        df['embedding'] = [str(i) for i in self._embeddings.create(records)]

        values = []
        for i, row in df.iterrows():
            embedding = row.pop('embedding')
            content = row.to_json()
            values.append((i, row['updated_at'], content, embedding))

        with self._db.cursor() as cursor:
            cursor.executemany(f'''
                INSERT INTO {table_name} (_index, updated_at, {content_column_name}, {vector_column_name})
                VALUES (%s, %s, %s, %s)
            ''', values)
            cursor.fetchall()

    def _sync_file(self, file: File, content_column_name: str, vector_column_name: str):
        table_name = File.serialize_name(file.name)
        is_synced = self._is_file_table_synced(table_name, file.updated_at)

        if is_synced:
            return table_name

        self._db.drop_table(table_name)
        self._create_file_table(table_name, content_column_name, vector_column_name)
        self._insert_file(file, table_name, content_column_name, vector_column_name)

        return table_name

    def sync_files(
        self,
        min_updated_at: Optional[int] = None,
        ignore_file_names: list[str] = [],
        content_column_name: str = 'content',
        vector_column_name: str = 'v',
    ):
        existed_table_names = self._db.get_table_names()
        file_table_names = []

        def handle_is_ignored_file(name: str, updated_at: int):
            if name in ignore_file_names or (min_updated_at and updated_at < min_updated_at):
                return True
            return False

        for file in self.get_files(handle_is_ignored_file):
            table_name = self._sync_file(file, content_column_name, vector_column_name)
            file_table_names.append(table_name)

        for existed_table_name in existed_table_names:
            if not existed_table_name in file_table_names:
                self._db.drop_table(existed_table_name)
