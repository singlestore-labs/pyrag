import singlestoredb as s2
from singlestoredb.connection import Connection

DBConnection = Connection


def connect(connection_url: str):
    return s2.connect(connection_url)
