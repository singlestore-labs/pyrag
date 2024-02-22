from typing import Optional
import singlestoredb as s2


class Database:
    def __init__(self, connection_url: str) -> None:
        self.connection_url = connection_url
        self.connection = s2.connect(self.connection_url)
        self.cursor = self.connection.cursor

    def create_table(
            self,
            table_name: str,
            definitions: Optional[list[tuple[str, Optional[str]]]] = None,
            definition: Optional[str] = None,
            extra: Optional[str] = None
    ):
        query_definitions = ''

        if definitions:
            for left, right in definitions:
                _definition = left
                if right:
                    _definition += f' {right}'
                query_definitions += f', {_definition}' if len(query_definitions) else _definition

        if definition:
            query_definitions += f', {definition}' if len(query_definitions) else definition

        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({query_definitions})'

        if extra:
            query += f' {extra}'

        with self.cursor() as cursor:
            cursor.execute(query)

    def drop_table(self, table_name: str):
        with self.cursor() as cursor:
            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

    def insert_values(self, table_name: str, values: list[dict], extra: Optional[str] = None):
        columns = ', '.join(values[0].keys())
        placeholders = ', '.join(['%s'] * len(values[0]))
        to_insert = [tuple(i.values()) for i in values]
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

        if extra:
            query += f' {extra}'

        with self.cursor() as cursor:
            cursor.executemany(query, to_insert)

    def delete_values(self, table_name: str, where: dict):
        placeholders = " AND ".join([f"{key} = %s" for key in where])
        values = tuple(where.values())
        query = f"DELETE FROM {table_name} WHERE {placeholders}"

        with self.cursor() as cursor:
            cursor.execute(query, values)
