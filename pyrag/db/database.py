from typing import Dict, List, Tuple
import singlestoredb as s2


class Database:
    def __init__(self, connection_url: str) -> None:
        self.connection_url = connection_url
        self.connection = s2.connect(self.connection_url)
        self.cursor = self.connection.cursor

    def create_table(self, table_name: str, columns: List[Tuple[str, str]]):
        column_definitions = ', '.join([f"{col_name} {data_type}" for col_name, data_type in columns])
        with self.cursor() as cursor:
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})')

    def drop_table(self, table_name: str):
        with self.cursor() as cursor:
            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

    def insert_values(self, table_name: str, values: List[Dict[str, str]]):
        columns = ', '.join(values[0].keys())
        placeholders = ', '.join(['%s'] * len(values[0]))
        to_insert = [tuple(i.values()) for i in values]

        with self.cursor() as cursor:
            cursor.executemany(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', to_insert)
