import os
import boto3
import torch
import numpy as np
import singlestoredb as s2
from transformers import AutoModel, AutoTokenizer
from dotenv import load_dotenv
from semantic_text_splitter import CharacterTextSplitter

# pip install singlestoredb boto3 transformers torch semantic-text-splitter python-dotenv --quiet

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL')
db_name = os.environ.get('DB_NAME') or connection_url.split('/')[-1] or 'pyreg'
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')

db_connection = s2.connect(connection_url)
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

text_splitter = CharacterTextSplitter(trim_chunks=False)


def create_embedding(input):
    input_ids = tokenizer(input, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        embedding = model(**input_ids).last_hidden_state.mean(dim=1).squeeze().tolist()
        return np.array(embedding, dtype='<f4')


def split_text(text: str):
    return text_splitter.chunks(text, 2048)


def s3_get_files():
    try:
        response = s3.list_objects_v2(Bucket=aws_bucket_name)
        files = response.get('Contents')

        if not files:
            return []

        return files
    except:
        return []


def s3_get_file_content(key: str):
    try:
        obj = s3.get_object(Bucket=aws_bucket_name, Key=key)
        content = obj['Body'].read().decode('utf-8')
        return content
    except:
        return ''
