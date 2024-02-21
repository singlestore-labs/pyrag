from typing import Optional
from pyrag.embeddings.typing import EmbeddingInput
from pyrag.search.creator import SearchCreator


class SemanticSearch(SearchCreator):
    def __call__(
        self,
        table_name: str,
        input: EmbeddingInput,
        limit: Optional[int] = 5,
        select: Optional[str] = 'content',
        vector_column_name: Optional[str] = 'v',
        as_name: Optional[str] = 'similarity',
        index_name: Optional[str] = 'vector_index',
    ):
        input_embedding = self.embeddings.embed(input)[0]
        v_length = len(input_embedding)

        with self.db.cursor() as cursor:
            query = f'''
                SELECT {select}, {vector_column_name} <*> '{input_embedding}' :> VECTOR({v_length}) AS {as_name}
                FROM {table_name}
            '''

            if index_name:
                query += f'ORDER BY {as_name} USE INDEX ({index_name}) DESC'
            else:
                query += f' ORDER BY {as_name} DESC'

            if limit:
                query += f' LIMIT {limit}'

            cursor.execute(query)
            return cursor.fetchall()
