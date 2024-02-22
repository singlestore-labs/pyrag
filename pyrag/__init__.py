import os
from typing import Optional
from pyrag.chat.manager import ChatManager
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.embeddings.typing import Embedder, EmbeddingModelName
from pyrag.search.search import Search


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

        self.db = Database(connection_url)
        embeddings = Embeddings(embedding_model_name, embedder)
        self.create_embeddings = embeddings.embed
        semantic_search = Search(self.db, embeddings, 'semantic')
        self.semantic_search = semantic_search.search
        chat_manager = ChatManager(self.db, embeddings, self.semantic_search)
        self.create_chat = chat_manager.create_chat
