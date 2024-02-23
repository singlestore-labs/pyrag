from typing import Optional
from singlestoredb import connect


class Database:
    def __init__(self, connection_url: str) -> None:
        self.connection_url = connection_url
        self.connection = connect(self.connection_url)
        self.cursor = self.connection.cursor

    def where_to_definition(self, where: dict) -> str:
        return " AND ".join([f"{key} = {value}" for key, value in where.items()])

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
                _definition += f' {right}' if right else ''
                query_definitions += f', {_definition}' if len(query_definitions) else _definition

        if definition:
            query_definitions += f', {definition}' if len(query_definitions) else definition

        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({query_definitions})'
        query += f' {extra}' if extra else ''

        with self.cursor() as cursor:
            try:
                cursor.execute(query)
            finally:
                cursor.close()

    def drop_table(self, table_name: str):
        with self.cursor() as cursor:
            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

    def insert_values(self, table_name: str, values: list[dict], extra: Optional[str] = None):
        columns = ', '.join(values[0].keys())
        placeholders = ', '.join(['%s'] * len(values[0]))
        to_insert = [tuple(i.values()) for i in values]
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        query += f' {extra}' if extra else ''

        with self.cursor() as cursor:
            try:
                cursor.executemany(query, to_insert)
            finally:
                cursor.close()

    def delete_values(self, table_name: str, where: dict):
        where_definition = self.where_to_definition(where)
        query = f"DELETE FROM {table_name} WHERE {where_definition}"

        with self.cursor() as cursor:
            try:
                cursor.execute(query)
            finally:
                cursor.close()
