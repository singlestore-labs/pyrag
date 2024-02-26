import os
from typing import Optional
from pyrag.chat.manager import ChatManager
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.embeddings.typing import Embed
from pyrag.search.semantic import SemanticSearch


class PyRAG:
    def __init__(
        self,
        connection_url: str,
        embedding_model_name: Optional[str] = None,
        embed: Optional[Embed] = None,
        openai_api_key: Optional[str] = None,
        huggingfacehub_api_token: Optional[str] = None,
    ):
        if openai_api_key:
            os.environ['PR_OPENAI_API_KEY'] = openai_api_key
        if huggingfacehub_api_token:
            os.environ['PR_HUGGINGFACEHUB_API_TOKEN'] = huggingfacehub_api_token

        self.db = Database(connection_url)
        embeddings = Embeddings(embedding_model_name, embed)
        self.create_embeddings = embeddings.create
        self.semantic_search = SemanticSearch(self.db, embeddings)
        chat_manager = ChatManager(self.db, embeddings, self.semantic_search)
        self.create_chat = chat_manager.create_chat
