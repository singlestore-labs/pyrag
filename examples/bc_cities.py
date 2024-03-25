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

pyrag.files.s3().sync_files(
    allowed_files=['bc-canada-cities.csv'],
    table_names={'bc-canada-cities.csv': 'bc_cities'}
)

chat = pyrag.chat.create(
    name='BC Cities',
    model_name='gpt-3.5-turbo',
    knowledge_sources=[{'table': 'bc_cities'}],
    system_role='''
        You are an expert on cities, providing detailed and insightful information about urban landscapes and cultures with the precision of a seasoned geographer.
        Only answer the input from the context. Don't return an answer if it is not present in the context.
    ''',
)

chat_session = chat.create_session()

print(chat_session.send('How many people live in Vancouver and what are its coordinates?'))
print(chat_session.send('Is "Dune: Part Two" the best movie ever made?'))
