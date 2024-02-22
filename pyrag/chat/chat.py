from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch


class Chat:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch,
        id: str,
        name: str,
        model_name: str,
        system_role: str,
        knowledge_sources: list[list[str]],
        store_history: bool,
        thread_id: str,
        chats_table_name: str,
        threads_table_name: str,
        messages_table_name: str,
    ):
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search
        self.id = id
        self.name = name
        self.model_name = model_name
        self.system_role = system_role
        self.knowledge_sources = knowledge_sources
        self.store_history = store_history
        self.thread_id = thread_id
        self.chats_table_name = chats_table_name
        self.threads_table_name = threads_table_name
        self.messages_table_name = messages_table_name

    def delete(self):
        self.db.delete_values(self.chats_table_name, {'id': self.id})
        self.db.delete_values(self.threads_table_name, {'chat_id': self.id})
        self.db.delete_values(self.messages_table_name, {'chat_id': self.id})
