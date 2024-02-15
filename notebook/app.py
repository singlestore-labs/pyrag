import io
import os
import re
import boto3
import torch
import numpy as np
import pandas as pd
import singlestoredb as s2
from typing import Callable, Hashable, List, Optional
from transformers import AutoModel, AutoTokenizer
from dotenv import load_dotenv
from semantic_text_splitter import CharacterTextSplitter

# pip install singlestoredb boto3 transformers torch semantic-text-splitter python-dotenv --quiet

load_dotenv()

connection_url = os.environ.get('DB_CONNECTION_URL') or ''
db_name = os.environ.get('DB_NAME') or connection_url.split('/')[-1] or 'pyrag'

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')

db_connection = s2.connect(connection_url)
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

text_splitter = CharacterTextSplitter(trim_chunks=False)


def create_table(table_name: str):
    with db_connection.cursor() as cursor:
        cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            content LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            created_at DATETIME,
            v VECTOR(384) NOT NULL
          )
        ''')

        cursor.execute(f'''
          ALTER TABLE {table_name} ADD VECTOR INDEX vector_index (v)
          INDEX_OPTIONS '{"index_type": "IVF_PQ", "nlist": 4000}'
        ''')

        cursor.fetchall()


def drop_table(table_name: str):
    with db_connection.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        cursor.fetchall()


def is_table_valid(table_name: str, last_created_at: str):
    print(table_name)

    def is_exists():
        try:
            with db_connection.cursor() as cursor:
                cursor.execute(f'''
                  SELECT TABLE_NAME
                  FROM INFORMATION_SCHEMA.TABLES
                  WHERE TABLE_SCHEMA = '{db_name}'
                  AND TABLE_NAME = '{table_name}'
                ''')
                return bool(len(cursor.fetchall()))
        except Exception as e:
            print(e)
            return False

    def is_latest():
        try:
            with db_connection.cursor() as cursor:
                cursor.execute(f'''
                  SELECT created_at FROM {table_name} LIMIT 1
                ''')
                result = cursor.fetchone()
                crated_at = result[0] if type(result) == tuple else ''
                print(crated_at)
        except Exception as e:
            print(e)
            return False

    return is_exists() and is_latest()


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


def prepare_df(
    df: pd.DataFrame,
    customize_row: Optional[Callable[[Hashable, pd.Series, pd.DataFrame], None]],
    reserved_keys: List[str] = []
):
    for i, row in df.iterrows():
        content = row.to_json()
        df.at[i, 'content'] = content
        embedding = create_embedding(content)
        df.at[i, 'embedding'] = str(embedding.tolist())

        if customize_row:
            customize_row(i, row, df)

    return df.drop(columns=[col for col in df.columns if col not in [*reserved_keys, 'content', 'embedding']])


def insert_df(df: pd.DataFrame, table_name: str):
    with db_connection.cursor() as cursor:
        cursor.executemany(f'''
            INSERT INTO {table_name} (id, content, v, created_at)
            VALUES (%s, %s, %s, %s)
        ''', df.to_records(index=True).tolist())
        cursor.fetchall()


def format_file_name(file_name):
    return re.sub(r'\W', '_', file_name)


def get_s3_files():
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

    files = []
    for file in get_files():
        file_name = file['Key']

        files.append({
            'name': file_name,
            'content': get_file_content(file_name),
            'updated_at': file['LastModified']
        })

    return files


def main():
    files = [*get_s3_files()][1:]

    for file in files:
        table_name = format_file_name(file['name'])

        if is_table_valid(table_name, file['updated_at']):
            continue

        df = file_content_to_df(file['content'], get_file_extension(file['name']))

        def customize_row(i: Hashable, row: pd.Series, df: pd.DataFrame):
            df.at[i, 'created_at'] = str(file['updated_at'])

        create_table(table_name)
        insert_df(prepare_df(df, customize_row=customize_row, reserved_keys=['created_at']), table_name)


main()
