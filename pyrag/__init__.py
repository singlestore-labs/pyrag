import os
from typing import Optional
from pyrag import db
from pyrag.embeddings.model import EmbeddingsModel
from pyrag.embeddings.typing import Embedder, EmbeddingModelName
from pyrag.search.model import SearchModel


class PyRAG:
    def __init__(
        self,
        connection_url: str,
        embedding_model_name: Optional[EmbeddingModelName] = None,
        embedder: Optional[Embedder] = None,
        openai_api_key: Optional[str] = None,
    ):
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key

        self.db_connection = db.connect(connection_url)
        embeddings_model = EmbeddingsModel(embedding_model_name, embedder)
        self.create_embeddings = embeddings_model.embed
        semantic_search_model = SearchModel(self.db_connection, embeddings_model, 'semantic')
        self.semantic_search = semantic_search_model.search
