import io
import os
from typing import Callable, Hashable, Optional
import boto3
import torch
import numpy as np
import pandas as pd
import singlestoredb as s2
from transformers import AutoModel, AutoTokenizer
from dotenv import load_dotenv
from semantic_text_splitter import CharacterTextSplitter

# pip install singlestoredb boto3 transformers torch semantic-text-splitter python-dotenv --quiet

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''
db_name = os.environ.get('DB_NAME') or connection_url.split('/')[-1] or 'pyreg'
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')

# db_connection = s2.connect(connection_url)
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


def get_file_extension(name: str):
    return os.path.splitext(name)[1][1:]


def file_content_to_df(content: str, extension: str):
    if extension == 'csv':
        return pd.read_csv(io.StringIO(content))

    raise ValueError('Unsupported file format')


def process_df(df: pd.DataFrame, customize_row: Optional[Callable[[Hashable, pd.Series, pd.DataFrame], None]]):
    for i, row in df.iterrows():
        input = row.to_json()
        df.at[i, 'input'] = input
        embedding = create_embedding(input)
        df.at[i, 'embedding'] = str(embedding.tolist())

        if customize_row:
            customize_row(i, row, df)

    return df


def insert_df(df: pd.DataFrame):
    print(df)
    return


def s3_process():
    def get_files():
        try:
            response = s3.list_objects_v2(Bucket=aws_bucket_name)
            files = response.get('Contents')

            if not files:
                return []

            return files
        except Exception as e:
            print(e)
            return []

    def get_file_content(key: str):
        try:
            obj = s3.get_object(Bucket=aws_bucket_name, Key=key)
            content = obj['Body'].read().decode('utf-8')
            return content
        except Exception as e:
            print(e)
            return ''

    for file in get_files()[1:]:
        file_name = file['Key']
        file_extention = get_file_extension(file_name)
        file_content = get_file_content(file_name)
        df = file_content_to_df(file_content, file_extention)

        def customize_row(i: Hashable, row: pd.Series, df: pd.DataFrame):
            df.at[i, 'created_at'] = file['LastModified']

        df = process_df(df, customize_row)
        insert_df(df)


def main():
    s3_process()


main()
