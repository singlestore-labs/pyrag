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

# chat_1 = pyrag.chat.create(
#     model_name='gpt-3.5-turbo',
#     name='French kitchen',
#     system_role="You are the owner of a French kitchen and help newbies cook. Answer in English with a French accent.",
#     store=True,
#     store_messages_history=True,
# )
# chat_1_session = chat_1.create_session(name='Cooking potatoes')
# print(chat_1_session.send('What is a potato?', retrive=False))
# print(chat_1_session.send('How to make it mashed?', retrive=False))

# chat_2 = pyrag.chat.create(
#     model_name='gpt-3.5-turbo',
#     name='Canada cities expert',
#     system_role="You're an expert on Canadian cities, answer the user's questions like a geographer.",
#     knowledge_tables=[['bc_canada_cities_csv']],
# )

# chat_2_session = chat_2.create_session()
# print(chat_2_session.send(
#     'What is Coquitlam?',
#     search_kwargs={
#         # 'min_similarity': 0.2,
#         # 'where': {'id': 1}
#     })
# )
# print(chat_2_session.send('How many people live there?', retrive=False))

# chat_2_session_2 = chat_2.create_session()
# print(chat_2_session_2.send('Prince George timezone'))


s3 = pyrag.files.s3()
for i in s3.get_files():
    pass
