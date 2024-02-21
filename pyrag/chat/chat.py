from typing import List, Optional
from pyrag.chat.knowledge_source import ChatKnowledgeSource
from pyrag.chat.typing import ChatMessagesTableName, ChatModelName, ChatName, ChatStoreMessages, ChatSystemRole, ChatTableName, ChatThreadId, ChatThreadsTableName
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch


class Chat:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch,
        knowledge_sources: List[ChatKnowledgeSource],
        name: Optional[ChatName] = None,
        model_name: Optional[ChatModelName] = None,
        table_name: Optional[ChatTableName] = 'chats',
        thread_id: Optional[ChatThreadId] = None,
        threads_table_name: Optional[ChatThreadsTableName] = 'chat_threads',
        system_role: Optional[ChatSystemRole] = 'You are a helpful assistant',
        store_messages: Optional[ChatStoreMessages] = True,
        messages_table_name: Optional[ChatMessagesTableName] = 'chat_messages'
    ):
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search
        self.knowledge_sources = knowledge_sources
        self.name = name
        self.model_name = model_name
        self.table_name = table_name
        self.thread_id = thread_id
        self.threads_table_name = threads_table_name
        self.system_role = system_role
        self.store_messages = store_messages
        self.messages_table_name = messages_table_name
