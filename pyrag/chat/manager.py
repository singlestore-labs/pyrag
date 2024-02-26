from typing import Optional
from pyrag.chat.chat import Chat
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch


class ChatManager:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch
    ):
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search

    def create_chat(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        model_name: Optional[str] = None,
        system_role: Optional[str] = None,
        knowledge_sources: Optional[list[list[str]]] = None,
        store: Optional[bool] = None,
        store_messages_history: Optional[bool] = None,
        chats_table_name: Optional[str] = None,
        sessions_table_name: Optional[str] = None,
        messages_table_name: Optional[str] = None,
    ):

        return Chat(
            db=self.db,
            embeddings=self.embeddings,
            semantic_search=self.semantic_search,
            id=id,
            name=name,
            model_name=model_name,
            system_role=system_role,
            knowledge_sources=knowledge_sources,
            store=store,
            store_messages_history=store_messages_history,
            chats_table_name=chats_table_name,
            sessions_table_name=sessions_table_name,
            messages_table_name=messages_table_name,
        )
