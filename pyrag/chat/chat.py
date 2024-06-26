from json import dumps
from typing import Any, Optional
from uuid import uuid4
from pyrag.chat.knowledge import KnowledgeSource
from pyrag.chat.model import ChatModel

from pyrag.chat.session import ChatSession
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.vector import VectorSearch


class Chat:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        vector_search: VectorSearch,

        id: Optional[int] = None,
        name: Optional[str] = None,
        model_name: Optional[str] = None,
        model_kwargs: Any = None,
        system_role: Optional[str] = None,
        knowledge_sources: list[KnowledgeSource] = [],
        store: Optional[bool] = None,
        store_messages_history: Optional[bool] = None,
        chats_table_name: Optional[str] = None,
        sessions_table_name: Optional[str] = None,
        messages_table_name: Optional[str] = None,
    ):
        self._db = db
        self._embeddings = embeddings
        self._vector_search = vector_search

        self.id = id or 0
        self.name = name or str(uuid4())
        self.model_name = model_name
        self.system_role = system_role or 'You are a helpful assistant'
        self.knowledge_sources = knowledge_sources or []
        self.store = store or False
        self.store_messages_history = store_messages_history or False
        self.chats_table_name = chats_table_name or 'chats'
        self.sessions_table_name = sessions_table_name or 'chat_sessions'
        self.messages_table_name = messages_table_name or 'chat_messages'

        if self.store:
            try:
                self._load()
            except:
                self._create_tables()
                self._insert()

        self.model = ChatModel()(
            model_name=self.model_name,
            model_kwargs=model_kwargs
        )

    def _create_tables(self):
        tables_to_create = []

        tables_to_create.append([
            self.chats_table_name,
            [
                ('id', 'BIGINT NOT NULL AUTO_INCREMENT'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('name', 'VARCHAR(256) NOT NULL'),
                ('model_name', 'VARCHAR(256)'),
                ('system_role', 'TEXT'),
                ('knowledge_tables', 'JSON'),
                ('store_messages_history', 'BOOL'),
                ('sessions_table_name', 'VARCHAR(256)'),
                ('messages_table_name', 'VARCHAR(256)')
            ],
            f'''
                KEY(id),
                SHARD KEY (name),
                CONSTRAINT {self.chats_table_name}_name_uk UNIQUE (name)
            '''
        ])

        if self.store_messages_history:
            tables_to_create.append([
                self.sessions_table_name,
                [
                    ('id', 'BIGINT NOT NULL AUTO_INCREMENT'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('name', 'VARCHAR(256) NOT NULL'),
                    ('chat_id', 'BIGINT')
                ],
                f'''
                    KEY(id),
                    SHARD KEY (name),
                    CONSTRAINT {self.sessions_table_name}_name_uk UNIQUE (name)
                '''
            ])

            tables_to_create.append([
                self.messages_table_name,
                [
                    ('id', 'BIGINT AUTO_INCREMENT PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'BIGINT'),
                    ('session_id', 'BIGINT'),
                    ('message', 'JSON')
                ],
            ])

        for table in tables_to_create:
            self._db.create_table(*table)

    def _insert(self):
        self._db.insert_values(self.chats_table_name, [{
            'name': self.name,
            'model_name': self.model_name,
            'system_role': self.system_role,
            'knowledge_tables': dumps(self.knowledge_sources),
            'store_messages_history': self.store_messages_history,
            'sessions_table_name': self.sessions_table_name,
            'messages_table_name': self.messages_table_name,
        }])

        with self._db.cursor() as cursor:
            try:
                cursor.execute(f"SELECT id FROM {self.chats_table_name} WHERE name = '{self.name}'")
                row = cursor.fetchone()
                if type(row) == tuple:
                    self.id = row[0]
                else:
                    raise Exception('Chat id not found')
            finally:
                cursor.close()

    def _load(self):
        query = f"SELECT * FROM {self.chats_table_name}"
        if self.id:
            query += f" WHERE id = {self.id}"
        else:
            query += f" WHERE name = '{self.name}'"

        with self._db.cursor() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if not row or not cursor.description:
                    raise Exception(f'Chat not found')
                for column, value in zip(cursor.description, row):
                    if column[0] == 'store_messages_history':
                        value = bool(value)
                    setattr(self, column[0], value)
            finally:
                cursor.close()

    def create_session(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        store: Optional[bool] = None
    ) -> ChatSession:

        return ChatSession(
            db=self._db,
            embeddings=self._embeddings,
            vector_search=self._vector_search,
            chat_id=self.id,
            model=self.model,
            store=store or self.store_messages_history,
            system_role=self.system_role,
            knowledge_sources=self.knowledge_sources,
            table_name=self.sessions_table_name,
            messages_table_name=self.messages_table_name,
            id=id,
            name=name,
        )

    def delete(self):
        for table in [self.sessions_table_name, self.messages_table_name]:
            self._db.delete_values(table, {'chat_id': self.id})
        self._db.delete_values(self.chats_table_name, {'id': self.id})
