import singlestoredb as s2

from pyrag.db.typing import DBConnection


def connect(connection_url: str) -> DBConnection:
    return s2.connect(connection_url)
