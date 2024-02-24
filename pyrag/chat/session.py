from typing import Optional
from uuid import uuid4

from pyrag.chat.chain import ChatChain
from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch


class ChatSession:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch,
        chat_id: int,
        table_name: str,
        messages_table_name: str,
        system_role: str,
        knowledge_sources: list[list[str]],
        store_history: bool,
        id: Optional[int] = None,
        name: Optional[str] = None,
        **chat_chain_kwargs
    ):
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search
        self.id = id or 0
        self.name = name or str(uuid4())
        self.chat_id = chat_id
        self.table_name = table_name
        self.messages_table_name = messages_table_name
        self.system_role = system_role
        self.knowledge_sources = knowledge_sources
        self.store_history = store_history
        self.message_history = None
        self.memory = None

        try:
            self._load()
        except:
            self._insert()

        if self.store_history:
            from langchain.memory import ConversationBufferMemory
            from pyrag.chat.message_history import ChatMessageHistory

            self.message_history = ChatMessageHistory(
                db=self.db,
                chat_id=self.chat_id,
                session_id=self.id,
                messages_table_name=self.messages_table_name
            )

            self.memory = ConversationBufferMemory(
                chat_memory=self.message_history,
                memory_key='chat_history',
                return_messages=True,
            )

        self.chain = ChatChain(
            memory=self.memory,
            system_role=self.system_role,
            **chat_chain_kwargs
        )

    def _insert(self):
        self.db.insert_values(self.table_name, [{
            'name': self.name,
            'chat_id': self.chat_id,
            'store_history': self.store_history
        }])

        with self.db.cursor() as cursor:
            try:
                cursor.execute(f"SELECT id FROM {self.table_name} WHERE name = '{self.name}'")
                row = cursor.fetchone()
                if type(row) == tuple:
                    self.id = row[0]
                else:
                    raise Exception('Chat session id not found')
            finally:
                cursor.close()

    def _load(self):
        query = f"SELECT * FROM {self.table_name}"
        if self.id:
            query += f" WHERE id = {self.id}"
        else:
            query += f" WHERE name = '{self.name}'"

        with self.db.cursor() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if not row or not cursor.description:
                    raise Exception(f'Chat session not found')
                for column, value in zip(cursor.description, row):
                    if column[0] == 'created_at':
                        continue
                    if column[0] == 'store_history':
                        value = bool(value)
                    setattr(self, column[0], value)
            finally:
                cursor.close()

    def send(self, prompt: str):
        print(prompt)

    def delete(self):
        self.db.delete_values(self.table_name, {'id': self.id})
        self.db.delete_values(self.messages_table_name, {'session_id': self.id})
