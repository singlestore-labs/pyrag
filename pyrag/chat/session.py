from typing import Optional
from uuid import uuid4
from pyrag.chat.message_history import ChatMessageHistory
from pyrag.db.database import Database
# from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


class ChatSession:
    def __init__(
        self, db: Database,
        chat_id: str,
        table_name: str,
        messages_table_name: str,
        id: Optional[str] = None,
    ):
        self.db = db
        self.id = id or ''
        self.chat_id = chat_id
        self.table_name = table_name
        self.messages_table_name = messages_table_name

        if not self.id:
            self.id = str(uuid4())
            self._insert()

        self.message_history = ChatMessageHistory(
            db=self.db,
            chat_id=self.chat_id,
            session_id=self.id,
            messages_table_name=self.messages_table_name
        )

    def _insert(self):
        self.db.insert_values(self.table_name, [{
            'id': self.id,
            'chat_id': self.chat_id
        }])

    def send(self, prompt: str):
        print(prompt)

    def delete(self):
        self.db.delete_values(self.table_name, {'id': self.id})
