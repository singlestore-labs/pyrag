from typing import Any, Callable
from singlestoredb.connection import Result


SearchInput = str
SearchResult = Result
Search = Callable[[Any], SearchResult]
