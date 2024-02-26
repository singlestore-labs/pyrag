from typing import Optional
from pyrag.search.base import BaseSearch
from pyrag.search.typing import SearchInput


class SemanticSearch(BaseSearch):
    def __call__(
        self,
        table_name: str,
        input: SearchInput,
        select: Optional[str] = 'content',
        where: Optional[dict] = None,
        limit: Optional[int] = 5,
        min_similarity: Optional[float] = 0,
        vector_column_name: Optional[str] = 'v',
        index_name: Optional[str] = 'vector_index',
    ):
        input_embedding = self.embeddings.create(input)[0]
        v_length = len(input_embedding)
        query = f'''
            SELECT {select}, {vector_column_name} <*> '{input_embedding}' :> VECTOR({v_length}) AS similarity
            FROM {table_name}
            WHERE similarity > {min_similarity}
        '''

        if where:
            where_definition = self.db.where_to_definition(where)
            query += f' AND {where_definition}'

        if index_name:
            query += f' ORDER BY similarity USE INDEX ({index_name}) DESC'
        else:
            query += f' ORDER BY similarity DESC'

        if limit:
            query += f' LIMIT {limit}'

        with self.db.cursor() as cursor:
            try:
                cursor.execute(query)
                return cursor.fetchall()
            finally:
                cursor.close()
