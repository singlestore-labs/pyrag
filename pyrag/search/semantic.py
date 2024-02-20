from typing import Optional
from ..db.typing import DBConnection
from ..embeddings.typing import CreateEmbeddings, EmbeddingInput


def semantic_search_factory(db_connection: DBConnection, create_embeddings: CreateEmbeddings):
    def semantic_search(
            table_name: str,
            input: EmbeddingInput,
            select: Optional[str] = 'content',
            vector_column_name: Optional[str] = 'v',
            as_name: Optional[str] = 'similarity',
            index_name: Optional[str] = 'vector_index',
            limit: Optional[int] = 5
    ):
        input_embedding = create_embeddings(input)[0]
        v_length = len(input_embedding)

        with db_connection.cursor() as cursor:
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

    return semantic_search
