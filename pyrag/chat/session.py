from typing import Any, Optional
from uuid import uuid4

from pyrag.db.database import Database
from pyrag.embeddings.embeddings import Embeddings
from pyrag.search.semantic import SemanticSearch
from pyrag.chat.chain import ChatChain, ChatModel


class ChatSession:
    def __init__(
        self,
        db: Database,
        embeddings: Embeddings,
        semantic_search: SemanticSearch,

        chat_id: int,
        model: ChatModel,
        store: bool,
        system_role: str,
        table_name: str,
        messages_table_name: str,
        id: Optional[int] = None,
        name: Optional[str] = None,
        knowledge_tables: Optional[list[list[str]]] = None,
    ):
        self.db = db
        self.embeddings = embeddings
        self.semantic_search = semantic_search

        self.chat_id = chat_id
        self.store = store or False
        self.system_role = system_role
        self.knowledge_tables = knowledge_tables or []
        self.table_name = table_name
        self.messages_table_name = messages_table_name
        self.id = id or 0
        self.name = name or str(uuid4())

        if self.store:
            try:
                self._load()
            except:
                self._insert()

        self.chain = ChatChain(
            db=self.db,
            model=model,
            chat_id=self.chat_id,
            session_id=self.id,
            store=self.store,
            messages_table_name=self.messages_table_name,
            system_role=self.system_role,
            include_context=bool(len(self.knowledge_tables))
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

    def _search_context(
        self,
        input: str,
        search_kwargs: dict[str, Any] = {}
    ):
        if not len(self.knowledge_tables):
            return None

        results = []

        for knowledge_table in self.knowledge_tables:
            if len(knowledge_table) > 1:
                search_kwargs['vector_column_name'] = search_kwargs.get('vector_column_name', knowledge_table[1])

            result = self.semantic_search(
                table_name=knowledge_table[0],
                input=input,
                **search_kwargs
            )

            if type(result) == list and len(result) and type(result[0]) == tuple:
                results.extend(result)

        results = sorted(results, key=lambda x: -x[1])
        return results[0] if len(results) else None

    def send(
        self,
        input: str,
        retrive: bool = True,
        search_kwargs: dict[str, Any] = {}
    ):
        context = ''

        if retrive:
            context = self._search_context(input, search_kwargs=search_kwargs) or context

        return self.chain.predict(input=input, context=context)

    def delete(self):
        self.db.delete_values(self.table_name, {'id': self.id})
        self.db.delete_values(self.messages_table_name, {'session_id': self.id})
