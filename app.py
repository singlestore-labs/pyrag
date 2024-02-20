import os
from pyrag import PyRAG
from dotenv import load_dotenv

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''
pyrag = PyRAG(connection_url)
