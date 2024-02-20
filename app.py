import os
from pyrag import PyRAG
from dotenv import load_dotenv

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''
pyrag = PyRAG(connection_url)

# print(pyrag.semantic_search('THE_STORY_THE_FIELD_GUIDE_pdf', 'concepts at the heart of Data Science'))
