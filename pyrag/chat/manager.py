from typing import List, Optional
from pyrag.chat.chat import Chat
from pyrag.chat.knowledge_source import ChatKnowledgeSource
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch
from pyrag.chat.typing import ChatMessagesTableName, ChatModelName, ChatName, ChatStoreMessages, ChatSystemRole, ChatTableName, ChatThreadId, ChatThreadsTableName


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

    def create(
        self,
        knowledge_sources: List[ChatKnowledgeSource],
        name: Optional[ChatName] = None,
        model_name: Optional[ChatModelName] = None,
        table_name: Optional[ChatTableName] = None,
        thread_id: Optional[ChatThreadId] = None,
        threads_table_name: Optional[ChatThreadsTableName] = None,
        system_role: Optional[ChatSystemRole] = None,
        store_messages: Optional[ChatStoreMessages] = None,
        messages_table_name: Optional[ChatMessagesTableName] = None
    ):
        return Chat(
            self.db,
            self.embeddings,
            self.semantic_search,
            knowledge_sources,
            name,
            model_name,
            table_name,
            thread_id,
            threads_table_name,
            system_role,
            store_messages,
            messages_table_name
        )
