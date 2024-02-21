import os
from pyrag import PyRAG
from dotenv import load_dotenv

from pyrag.chat.knowledge_source import ChatKnowledgeSource

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''
pyrag = PyRAG(connection_url)
# print(pyrag.create_embeddings('123'))
# print(pyrag.semantic_search('THE_STORY_THE_FIELD_GUIDE_pdf', 'concepts at the heart of Data Science'))
chat = pyrag.create_chat([ChatKnowledgeSource('bc_canada_cities_csv')])
