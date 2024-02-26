from typing import Optional
from uuid import uuid4
from langchain.memory import ConversationBufferMemory

from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch
from pyrag.chat.chain import ChatLLMChain
from pyrag.chat.model import ChatModel


class ChatSession:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch,

        chat_id: int,
        store: bool,
        system_role: str,
        table_name: str,
        messages_table_name: str,
        id: Optional[int] = None,
        name: Optional[str] = None,
    ):
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search

        self.chat_id = chat_id
        self.store = store
        self.system_role = system_role
        self.table_name = table_name
        self.messages_table_name = messages_table_name
        self.id = id or 0
        self.name = name or str(uuid4())

        self.message_history = None
        self.memory = None

        if self.store:
            try:
                self._load()
            except:
                self._insert()

            from pyrag.chat.db_message_history import ChatDatabaseMessageHistory
            self.message_history = ChatDatabaseMessageHistory(
                db=self.db,
                chat_id=self.id,
                session_id=self.id,
                messages_table_name=self.messages_table_name
            )
        else:
            from langchain.memory import ChatMessageHistory
            self.message_history = ChatMessageHistory()

        self.memory = ConversationBufferMemory(
            chat_memory=self.message_history,
            memory_key='chat_history',
            return_messages=True,
        )

        self.chain = ChatLLMChain(
            model=ChatModel(),
            memory=self.memory,
            system_role=self.system_role,
        )

    def _insert(self):
        self.db.insert_values(self.table_name, [{
            'name': self.name,
            'chat_id': self.chat_id,
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
                    setattr(self, column[0], value)
            finally:
                cursor.close()

    def delete(self):
        self.db.delete_values(self.table_name, {'id': self.id})
        self.db.delete_values(self.messages_table_name, {'session_id': self.id})
