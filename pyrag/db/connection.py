import singlestoredb as s2

from .typing import DBConnection


def connect(connection_url: str) -> DBConnection:
    return s2.connect(connection_url)
