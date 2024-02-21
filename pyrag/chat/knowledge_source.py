from typing import Optional


class ChatKnowledgeSource:
    def __init__(
        self,
        table_name: str,
        content_column: Optional[str] = 'content',
        vector_column: Optional[str] = 'v'
    ):
        self.table_name = table_name
        self.content_column = content_column
        self.vector_column = vector_column
