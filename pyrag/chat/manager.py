from json import dumps
from uuid import uuid4

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

    def _create_tables(
        self,
        chats_table_name: str,
        threads_table_name: str,
        messages_table_name: str,
        store_history: bool
    ):
        tables_to_create = []

        tables_to_create.append([
            chats_table_name,
            [
                ('id', 'VARCHAR(256) PRIMARY KEY'),
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

        if store_history:
            tables_to_create.append([
                threads_table_name,
                [
                    ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'VARCHAR(256)')
                ],
            ])

            tables_to_create.append([
                messages_table_name,
                [
                    ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'VARCHAR(256)'),
                    ('chat_thread_id', 'INT'),
                    ('content', 'LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci'),
                    ('role', 'VARCHAR(256)')
                ],
            ])

        for table in tables_to_create:
            self.db.create_table(*table)

    def _insert_chat(
        self,
        chats_table_name: str,
        id: str,
        name: str,
        model_name: str,
        system_role: str,
        knowledge_sources: list[list[str]],
        store_history: bool,
        threads_table_name: str,
        messages_table_name: str
    ):
        self.db.insert_values(chats_table_name, [{
            'id': id,
            'name': name,
            'model_name': model_name,
            'system_role': system_role,
            'knowledge_sources': dumps(knowledge_sources),
            'store_history': store_history,
            'threads_table_name': threads_table_name,
            'messages_table_name': messages_table_name,
        }])

    def create_chat(
        self,
        id: str = str(uuid4()),
        name: str = '',
        model_name: str = 'gpt-3.5-turbo',
        system_role: str = 'You are a helpful assistant',
        knowledge_sources: list[list[str]] = [],
        store_history: bool = False,
        thread_id: str = '',
        chats_table_name: str = 'chats',
        threads_table_name: str = 'chat_threads',
        messages_table_name: str = 'chat_messages',
    ):

        if not thread_id:
            self._create_tables(
                chats_table_name,
                threads_table_name,
                messages_table_name,
                store_history
            )

            self._insert_chat(
                chats_table_name,
                id,
                name,
                model_name,
                system_role,
                knowledge_sources,
                store_history,
                threads_table_name,
                messages_table_name
            )

        return Chat(
            self.db,
            self.embeddings,
            self.semantic_search,
            id,
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
