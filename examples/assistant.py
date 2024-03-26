import os

from pyrag import PyRAG
from dotenv import load_dotenv

load_dotenv()

pyrag = PyRAG(
    connection_url=os.environ.get('DB_CONNECTION_URL', ''),
    embedding_model_name='text-embedding-3-small',
    openai_api_key=os.environ.get('OPENAI_API_KEY', ''),
)

pyrag.files.s3().sync_files(
    allowed_files=['stars.csv'],
)

chat = pyrag.chat.create(
    id=1,
    model_name='gpt-3.5-turbo',
    knowledge_sources=[{'table': 'stars_csv'}],
    store=True,
    store_messages_history=True
)

chat_session = chat.create_session(id=1)

print(chat_session.send('What is Polaris?'))
print(chat_session.send('What was my last question?', retrive=False))
print(chat_session.send('What else can you tell me about this star?', retrive=False))
