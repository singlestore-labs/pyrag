import os

from pyrag import PyRAG
from dotenv import load_dotenv

load_dotenv()

pyrag = PyRAG(
    connection_url=os.environ.get('DB_CONNECTION_URL', ''),
    huggingfacehub_api_token=os.environ.get('HUGGINGFACEHUB_API_TOKEN')
)

pyrag.files.s3().sync_files(
    allowed_files=['paragraph.txt'],
    table_names={'paragraph.txt': 'hf_paragraph_txt'}
)

chat = pyrag.chat.create(
    knowledge_sources=[{'table': 'hf_paragraph_txt'}],
)

chat_session = chat.create_session()

print(chat_session.send('What is this text about?'))
print(chat_session.send('What was my last question?', retrive=False))
