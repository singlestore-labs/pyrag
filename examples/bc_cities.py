import os

from pyrag import PyRAG
from dotenv import load_dotenv

load_dotenv()

pyrag = PyRAG(
    connection_url=os.environ.get('DB_CONNECTION_URL', ''),
    embedding_model_name='text-embedding-3-small',
    openai_api_key=os.environ.get('OPENAI_API_KEY', ''),
)

pyrag.files.s3(
    access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', ''),
    secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
    bucket_name=os.environ.get('AWS_BUCKET_NAME', ''),
).sync_files(
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
