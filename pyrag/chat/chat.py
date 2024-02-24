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
        id: Optional[int] = None,
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
        self.id = id or 0
        self.name = name or str(uuid4())
        self.model_name = model_name or 'gpt-3.5-turbo'
        self.system_role = system_role or 'You are a helpful assistant'
        self.knowledge_sources = knowledge_sources or []
        self.store_history = store_history or True
        self.chats_table_name = chats_table_name or 'chats'
        self.sessions_table_name = sessions_table_name or 'chat_sessions'
        self.messages_table_name = messages_table_name or 'chat_messages'

        try:
            self._load()
        except:
            self._create_tables()
            self._insert()

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
                ('knowledge_sources', 'JSON'),
                ('store_history', 'BOOL'),
                ('sessions_table_name', 'VARCHAR(256)'),
                ('messages_table_name', 'VARCHAR(256)')
            ],
            f'''
                KEY(id),
                SHARD KEY (name),
                CONSTRAINT {self.chats_table_name}_name_uk UNIQUE (name)
            '''
        ])

        if self.store_history:
            tables_to_create.append([
                self.sessions_table_name,
                [
                    ('id', 'BIGINT NOT NULL AUTO_INCREMENT'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('name', 'VARCHAR(256) NOT NULL'),
                    ('chat_id', 'BIGINT'),
                    ('store_history', 'BOOL')
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
            self.db.create_table(*table)

    def _insert(self):
        self.db.insert_values(self.chats_table_name, [{
            'name': self.name,
            'model_name': self.model_name,
            'system_role': self.system_role,
            'knowledge_sources': dumps(self.knowledge_sources),
            'store_history': self.store_history,
            'sessions_table_name': self.sessions_table_name,
            'messages_table_name': self.messages_table_name,
        }])

        with self.db.cursor() as cursor:
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

        with self.db.cursor() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if not row or not cursor.description:
                    raise Exception(f'Chat not found')
                for column, value in zip(cursor.description, row):
                    if column[0] == 'created_at':
                        continue
                    if column[0] == 'store_history':
                        value = bool(value)
                    setattr(self, column[0], value)
            finally:
                cursor.close()

    def create_session(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        stor_history: Optional[bool] = None,
        **chat_chain_kwargs,
    ) -> ChatSession:
        return ChatSession(
            db=self.db,
            embeddings=self.embeddings,
            semantic_search=self.semantic_search,
            id=id,
            name=name,
            chat_id=self.id,
            table_name=self.sessions_table_name,
            messages_table_name=self.messages_table_name,
            system_role=self.system_role,
            knowledge_sources=self.knowledge_sources,
            store_history=stor_history or self.store_history,
            **chat_chain_kwargs
        )

    def delete(self):
        for table in [self.sessions_table_name, self.messages_table_name]:
            self.db.delete_values(table, {'chat_id': self.id})
        self.db.delete_values(self.chats_table_name, {'id': self.id})
