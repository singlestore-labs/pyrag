from json import dumps
from typing import Optional
from uuid import uuid4
from pyrag.chat.session import ChatSession
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch


class Chat:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch,
        id: Optional[str] = None,
        name: Optional[str] = None,
        model_name: Optional[str] = None,
        system_role: Optional[str] = None,
        knowledge_sources: Optional[list[list[str]]] = None,
        store_history: Optional[bool] = None,
        chats_table_name: Optional[str] = None,
        sessions_table_name: Optional[str] = None,
        messages_table_name: Optional[str] = None,
    ):
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search
        self.id = id or ''
        self.name = name or ''
        self.model_name = model_name or 'gpt-3.5-turbo'
        self.system_role = system_role or 'You are a helpful assistant'
        self.knowledge_sources = knowledge_sources or []
        self.store_history = store_history or True
        self.chats_table_name = chats_table_name or 'chats'
        self.sessions_table_name = sessions_table_name or 'chat_sessions'
        self.messages_table_name = messages_table_name or 'chat_messages'

        if not self.id:
            self.id = str(uuid4())
            self._create_tables()
            self._insert()

    def _create_tables(self):
        tables_to_create = []

        tables_to_create.append([
            self.chats_table_name,
            [
                ('id', 'VARCHAR(256) PRIMARY KEY'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('name', 'VARCHAR(256)'),
                ('model_name', 'VARCHAR(256)'),
                ('system_role', 'TEXT'),
                ('knowledge_sources', 'JSON'),
                ('store_history', 'BOOL'),
                ('sessions_table_name', 'VARCHAR(256)'),
                ('messages_table_name', 'VARCHAR(256)')
            ]
        ])

        if self.store_history:
            tables_to_create.append([
                self.sessions_table_name,
                [
                    ('id', 'VARCHAR(256) PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'VARCHAR(256)')
                ],
            ])

            tables_to_create.append([
                self.messages_table_name,
                [
                    ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'VARCHAR(256)'),
                    ('session_id', 'VARCHAR(256)'),
                    ('message', 'JSON')
                ],
            ])

        for table in tables_to_create:
            self.db.create_table(*table)

    def _insert(self):
        self.db.insert_values(self.chats_table_name, [{
            'id': self.id,
            'name': self.name,
            'model_name': self.model_name,
            'system_role': self.system_role,
            'knowledge_sources': dumps(self.knowledge_sources),
            'store_history': self.store_history,
            'sessions_table_name': self.sessions_table_name,
            'messages_table_name': self.messages_table_name,
        }])

    def create_session(self, id: Optional[str] = None) -> ChatSession:
        return ChatSession(
            db=self.db,
            id=id,
            chat_id=self.id,
            table_name=self.sessions_table_name,
            messages_table_name=self.messages_table_name
        )

    def delete(self):
        self.db.delete_values(self.chats_table_name, {'id': self.id})
        self.db.delete_values(self.sessions_table_name, {'chat_id': self.id})
        self.db.delete_values(self.messages_table_name, {'chat_id': self.id})
