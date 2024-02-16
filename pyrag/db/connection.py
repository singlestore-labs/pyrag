import singlestoredb as s2


def connect(connection_url: str):
    return s2.connect(connection_url)
