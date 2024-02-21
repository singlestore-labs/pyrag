from typing import List, Optional

from ..db.typing import DBConnection
from ..embeddings.typing import CreateEmbeddings

from .typing import ChatKnowledgeSource


class ChatFactory:
    def __init__(
        self,
        db_connection: DBConnection,
        create_embeddings: CreateEmbeddings,
        semantic_search,
    ) -> None:
        pass

    def chat(
        self,
        knowledge_sources=List[ChatKnowledgeSource],
        id: Optional[str] = None,
        model_name: Optional[str] = None,
        table_name: Optional[str] = 'chats',
        thread_id: Optional[str] = None,
        threads_table_name: Optional[str] = 'chat_threads',
        system_role: Optional[str] = 'You are a helpful assistant',
        store_messages: Optional[bool] = True,
        messages_table_name: Optional[str] = 'chat_messages'
    ) -> None:
        pass
