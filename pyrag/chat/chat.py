from typing import List, Optional
from pyrag.chat.typing import ChatKnowledgeSource, ChatMessagesTableName, ChatModelName, ChatName, ChatStoreHistory, ChatSystemRole, ChatTableName, ChatThreadId, ChatThreadsTableName
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch


class Chat:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch,
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
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search
        self.name = name
        self.model_name = model_name
        self.system_role = system_role or 'You are a helpful assistant'
        self.knowledge_sources = knowledge_sources
        self.store_history = store_history
        self.thread_id = thread_id
        self.chats_table_name = chats_table_name or 'chats'
        self.threads_table_name = threads_table_name or 'chat_threads'
        self.messages_table_name = messages_table_name or 'chat_messages'

        self._create_tables()

    def _create_tables(self):
        tables_to_create = []

        tables_to_create.append([
            self.chats_table_name,
            [
                ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('name', 'VARCHAR(256)'),
                ('model_name', 'VARCHAR(256)'),
                ('system_role', 'TEXT'),
                ('knowledge_sources', 'JSON'),
                ('store_history', 'BOOL'),
                ('threads_table_name', 'VARCHAR(256)'),
                ('messages_table_name', 'VARCHAR(256)')
            ]
        ])

        if self.store_history:
            tables_to_create.append([
                self.threads_table_name,
                [
                    ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'INT')
                ],
            ])

            tables_to_create.append([
                self.messages_table_name,
                [
                    ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'INT'),
                    ('chat_thread_id', 'INT'),
                    ('content', 'LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci'),
                    ('role', 'VARCHAR(256)')
                ],
            ])

        for table in tables_to_create:
            self.db.create_table(*table)
