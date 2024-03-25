import os

from pyrag import PyRAG
from dotenv import load_dotenv

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''

pyrag = PyRAG(
    connection_url,
    embedding_model_name='text-embedding-3-small',
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
)

pyrag.files.url.sync_file(url="https://www.gutenberg.org/cache/epub/48320/pg48320.txt", table_name='sherlock')

chat = pyrag.chat.create(
    name='Sherlock',
    model_name='gpt-3.5-turbo',
    knowledge_sources=[{'table': 'sherlock'}],
    system_role='''
        You are a knowledgeable guide, answering inputs with insights and explanations inspired by the book, in the manner of a thoughtful and engaging teacher.
        Only answer the input from the context. Don't return an answer if it is not present in the context.
    ''',
    store=True,
    store_messages_history=True
)

chat_session = chat.create_session(name='Sherlock Bio')

print(chat_session.send('Who is Sherlock?'))
print(chat_session.send('How old is he?'))
print(chat_session.send('Who is Batman?'))
