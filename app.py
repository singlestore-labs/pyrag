import os
from pyrag import PyRAG
from dotenv import load_dotenv


load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''

pyrag = PyRAG(connection_url, )

# pyrag.db.connection
# pyrag.db.cursor
# pyrag.db.create_table('table_name', [('column_name', 'type')])
# pyrag.db.drop_table('table_name')
# pyrag.db.insert_values('table', [{'column': 'value'}])
# print(pyrag.semantic_search('bc_canada_cities_csv', 'Vancouver'))
# print(pyrag.create_embeddings('Some text here'))

# pyrag.db.drop_table('chats')
# pyrag.db.drop_table('chat_sessions')
# pyrag.db.drop_table('chat_messages')

# chat = pyrag.create_chat(
#     knowledge_sources=[['bc_canada_cities_csv']]
# )

chat = pyrag.create_chat(
    id='a5506e58-450b-4f57-9265-036060cf0d78'
)
