from json import dumps

from typing import List
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

        if store_history:
            tables_to_create.append([
                threads_table_name,
                [
                    ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
                    ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                    ('chat_id', 'INT')
                ],
            ])

            tables_to_create.append([
                messages_table_name,
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

    def _insert_chat(
        self,
        chats_table_name: str,
        name: str,
        model_name: str,
        system_role: str,
        knowledge_sources: List[List[str]],
        store_history: bool,
        threads_table_name: str,
        messages_table_name: str
    ):
        self.db.insert_values(chats_table_name, [{
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
        name: str = str(uuid4()),
        model_name: str = 'gpt-3.5-turbo',
        system_role: str = 'You are a helpful assistant',
        knowledge_sources: List[List[str]] = [],
        store_history: bool = False,
        thread_id: str = '',
        chats_table_name: str = 'chats',
        threads_table_name: str = 'chat_threads',
        messages_table_name: str = 'chat_messages',
    ):
        chat = Chat(
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

        if not thread_id:
            self._create_tables(
                chat.chats_table_name,
                chat.threads_table_name,
                chat.messages_table_name,
                chat.store_history
            )

            self._insert_chat(
                chat.chats_table_name,
                chat.name,
                chat.model_name,
                chat.system_role,
                chat.knowledge_sources,
                chat.store_history,
                chat.threads_table_name,
                chat.messages_table_name
            )

        return chat
