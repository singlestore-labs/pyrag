from typing import Optional
import db
import embeddings


class PyRAG:
    def __init__(self, connection_url: str, embedding_model: Optional[str]):
        self.db_connection = db.connect(connection_url)
        self.create_embeddings = embeddings.create_factory(embedding_model)
