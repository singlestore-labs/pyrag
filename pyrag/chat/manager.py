from typing import Any, Optional
from pyrag.chat.chat import Chat
from pyrag.chat.knowledge import KnowledgeSource
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.vector import VectorSearch


class ChatManager:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        vector_search: VectorSearch
    ):
        self._db = db
        self._embeddings = embeddings
        self._vector_search = vector_search

    def create(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        model_name: Optional[str] = None,
        model_kwargs: dict[str, Any] = {},
        system_role: Optional[str] = None,
        knowledge_sources: list[KnowledgeSource] = [],
        store: Optional[bool] = None,
        store_messages_history: Optional[bool] = None,
        chats_table_name: Optional[str] = None,
        sessions_table_name: Optional[str] = None,
        messages_table_name: Optional[str] = None,
    ):

        return Chat(
            db=self._db,
            embeddings=self._embeddings,
            vector_search=self._vector_search,
            id=id,
            name=name,
            model_name=model_name,
            model_kwargs=model_kwargs,
            system_role=system_role,
            knowledge_sources=knowledge_sources,
            store=store,
            store_messages_history=store_messages_history,
            chats_table_name=chats_table_name,
            sessions_table_name=sessions_table_name,
            messages_table_name=messages_table_name,
        )
