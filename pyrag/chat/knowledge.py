from typing import Optional, TypedDict


class KnowledgeSource(TypedDict, total=False):
    table: str
    content_column: Optional[str]
    vector_column: Optional[str]
