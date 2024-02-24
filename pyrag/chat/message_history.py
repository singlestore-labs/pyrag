from typing import Sequence
from json import dumps
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from pyrag.db.database import Database


class ChatMessageHistory(BaseChatMessageHistory):
    def __init__(
        self,
        db: Database,
        chat_id: int,
        session_id: int,
        messages_table_name: str,
    ):
        self.db = db
        self.chat_id = chat_id
        self.session_id = session_id
        self.messages_table_name = messages_table_name

    @property
    def messages(self):
        messages: Sequence[dict] = []
        with self.db.cursor() as cursor:
            try:
                cursor.execute(f'''
                  SELECT message FROM {self.messages_table_name}
                  WHERE session_id = {self.session_id}
                ''')
                for row in cursor.fetchall():
                    if type(row) == tuple:
                        messages.append(row[0])
            finally:
                cursor.close()

        return messages_from_dict(messages)

    def add_message(self, message: BaseMessage) -> None:
        self.db.insert_values(self.messages_table_name, [{
            'chat_id': self.chat_id,
            'session_id': self.session_id,
            'message': dumps(message_to_dict(message)),
        }])

    def clear(self) -> None:
        self.db.delete_values(self.messages_table_name, {
            'session_id': self.session_id
        })
