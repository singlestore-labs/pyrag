import os
import db
import embeddings
from typing import Optional


class PyRAG:
    def __init__(
            self,
            connection_url: str,
            embedding_model: embeddings.EmbeddingModelName = None,
            openai_api_key: Optional[str] = None,
    ):
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key

        self.db_connection = db.connect(connection_url)
        self.create_embeddings = embeddings.create_factory(embedding_model)
