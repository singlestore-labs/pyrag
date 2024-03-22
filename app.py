import os

from pyrag import PyRAG
from dotenv import load_dotenv

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''

pyrag = PyRAG(
    connection_url,
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
    huggingfacehub_api_token=os.environ.get('HUGGINGFACEHUB_API_TOKEN'),
)

# pyrag.db.connection
# pyrag.db.cursor
# pyrag.db.create_table('table', [('column_name', 'type')])
# pyrag.db.drop_table('table')
# pyrag.db.insert_values('table', [{'column': 'value'}])
# pyrag.db.delete_values('table', {'id': '1'})
# print(pyrag.vector_search('bc_canada_cities_csv', 'Coquitlam'))
# print(pyrag.embeddings.create('Some text here'))
# pyrag.db.drop_table('chats')
# pyrag.db.drop_table('chat_sessions')
# pyrag.db.drop_table('chat_messages')

# pyrag.db.drop_table('dataset_m_products_json')
# pyrag.files.url.sync_file(
#     "https://raw.githubusercontent.com/singlestore-labs/kai-estore/main/apps/server/src/data/dataset-m/dataset-m-products.json",
# )

# pyrag.files.s3().sync_files()

# chat = pyrag.chat.create(
#     model_name='gpt-3.5-turbo',
#     name='Canada cities expert',
#     system_role="You're an expert on Canadian cities, answer the user's questions like a geographer.",
#     knowledge_tables=[['bc_canada_cities_csv']],
# )

# chat_session = chat.create_session()
# response = chat_session.send('Coquitlam city')
# print(response)
