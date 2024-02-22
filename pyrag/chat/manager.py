from typing import List, Optional
from pyrag.chat.chat import Chat
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch
from pyrag.chat.typing import ChatKnowledgeSource, ChatMessagesTableName, ChatModelName, ChatName, ChatStoreHistory, ChatSystemRole, ChatTableName, ChatThreadId, ChatThreadsTableName


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
        name: Optional[ChatName] = None,
        model_name: Optional[ChatModelName] = None,
        system_role: Optional[ChatSystemRole] = None,
        knowledge_sources: Optional[List[ChatKnowledgeSource]] = None,
        store_history: Optional[ChatStoreHistory] = False,
        thread_id: Optional[ChatThreadId] = None,
        chats_table_name: Optional[ChatTableName] = None,
        threads_table_name: Optional[ChatThreadsTableName] = None,
        messages_table_name: Optional[ChatMessagesTableName] = None
    ):
        return Chat(
            self.db,
            self.embeddings,
            self.semantic_search,
            name,
            model_name,
            system_role,
            knowledge_sources,
            store_history,
            thread_id,
            chats_table_name,
            threads_table_name,
            messages_table_name,
        )
