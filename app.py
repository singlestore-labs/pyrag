import os
from pyrag import PyRAG
from dotenv import load_dotenv


load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''

pyrag = PyRAG(
    connection_url,
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
    huggingfacehub_api_token=os.environ.get('HUGGINGFACEHUB_API_TOKEN'),
    embedding_model_name='sentence-transformers/all-mpnet-base-v2',
)

# pyrag.db.connection
# pyrag.db.cursor
# pyrag.db.create_table('table', [('column_name', 'type')])
# pyrag.db.drop_table('table')
# pyrag.db.insert_values('table', [{'column': 'value'}])
# pyrag.db.delete_values('table', {'id': '1'})
# print(pyrag.semantic_search('bc_canada_cities_csv', 'Vancouver'))
# print(pyrag.create_embeddings('Some text here'))

# pyrag.db.drop_table('chats')
# pyrag.db.drop_table('chat_sessions')
# pyrag.db.drop_table('chat_messages')

chat = pyrag.create_chat(
    name='French kitchen',
    # model_name='gpt-3.5-turbo',
    # system_role="You are the owner of a French kitchen and help newbies cook. Answer in English with a French accent.",
    # store=True,
    # store_messages_history=True,
)

chat_session = chat.create_session(name='Cooking potatoes')
print(chat_session.send('What is a potato?'))
print(chat_session.send('How to make it mashed?'))
