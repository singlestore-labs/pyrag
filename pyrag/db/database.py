import singlestoredb as s2


class Database:
    def __init__(self, connection_url: str) -> None:
        self.connection_url = connection_url
        self.connection = s2.connect(self.connection_url)
        self.cursor = self.connection.cursor

    def create_table(self, table_name: str):
        with self.cursor() as cursor:
            pass
