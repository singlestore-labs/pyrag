# # PyRAG Live Data

# This notebook gets files from a S3 bucket, creates embeddings and inserts them into the database.

# Supported file types: csv, json, pdf, txt
# Supported S3 actions: upload, update, delete

# - Loading a new file, a new table is created.
# - Updating a file, a table is deleted and created anew.
# - Deleting a file, a table is deleted.

# %pip install singlestoredb boto3 transformers torch pandas==2.1.4 semantic-text-splitter python-dotenv PyPDF2 --quiet

import io
import os
import re
import boto3
import torch
import numpy as np
import pandas as pd
import singlestoredb as s2
from typing import Any, Callable, Hashable, List, Optional
from transformers import AutoModel, AutoTokenizer
from datetime import datetime, timezone
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from semantic_text_splitter import CharacterTextSplitter


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


def split_text(text: str):
    return text_splitter.chunks(text, 2048)


def get_file_extension(name: str):
    return os.path.splitext(name)[1][1:]


def create_embedding(input):
    input_ids = tokenizer(input, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        embedding = model(**input_ids).last_hidden_state.mean(dim=1).squeeze().tolist()
        return np.array(embedding, dtype='<f4')


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
          INDEX_OPTIONS '{{"index_type": "IVF_PQ", "nlist": 4000}}'
        ''')

        cursor.fetchall()


def drop_table(table_name: str):
    with db_connection.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        cursor.fetchall()


def get_table_names(table_name: str | None = None):
    try:
        with db_connection.cursor() as cursor:
            query = f'''
              SELECT TABLE_NAME
              FROM INFORMATION_SCHEMA.TABLES
              WHERE TABLE_SCHEMA = '{db_name}'
            '''

            if table_name:
                query += f" AND TABLE_NAME = '{table_name}'"

            cursor.execute(query)
            result = cursor.fetchall()

            if result:
                return [i[0] if type(i) == tuple else '' for i in result]

            return []
    except Exception as e:
        print(e)
        return []


def is_table_up_to_date(table_name: str, created_at: datetime):
    def is_exists():
        try:
            return bool(len(get_table_names(table_name)))
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

                if not type(result) == tuple:
                    return False

                return result[0] >= created_at
        except Exception as e:
            print(e)
            return False

    return is_exists() and is_latest()


def file_content_to_df(content: Any, extension: str):
    def assign_created_at(df: pd.DataFrame):
        df['created_at'] = datetime.now().astimezone(timezone.utc).replace(tzinfo=None)

    if extension == 'csv':
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        assign_created_at(df)
        return df

    if extension == 'json':
        df = pd.read_json(io.StringIO(content.decode('utf-8')))
        assign_created_at(df)
        return df

    if extension == 'pdf':
        text = ''
        reader = PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text += page.extract_text()
        df = pd.DataFrame(split_text(text), columns=['text'])
        assign_created_at(df)
        return df

    if extension == 'txt':
        df = pd.DataFrame(split_text(content.decode('utf-8')), columns=['text'])
        assign_created_at(df)
        return df

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
            INSERT INTO {table_name} (id, created_at, content, v)
            VALUES (%s, %s, %s, %s)
        ''', df.to_records(index=True).tolist())
        cursor.fetchall()


def format_file_name(file_name):
    return re.sub(r'\W', '_', file_name)


def s3_process_files(on_file):
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
            content = obj['Body'].read()
            return content
        except Exception as e:
            print(e)
            return ''

    for file in get_files():
        file_name = file['Key']

        on_file({
            'name': file_name,
            'content': get_file_content(file_name),
            'updated_at': datetime.strptime(
                str(file['LastModified']), '%Y-%m-%d %H:%M:%S%z'
            ).astimezone(timezone.utc).replace(tzinfo=None)
        })


def main():
    existed_table_names = get_table_names()
    file_table_names = []

    def on_file(file):
        table_name = format_file_name(file['name'])
        file_table_names.append(table_name)

        if is_table_up_to_date(table_name, file['updated_at']):
            print(table_name, 'is up to date')
            return

        df = file_content_to_df(file['content'], get_file_extension(file['name']))

        drop_table(table_name)
        create_table(table_name)

        def customize_row(i: Hashable, _, df: pd.DataFrame):
            df.at[i, 'created_at'] = file['updated_at']

        insert_df(prepare_df(df, customize_row=customize_row, reserved_keys=['created_at']), table_name)
        print(table_name, 'updated' if table_name in existed_table_names else 'inserted')

    for file_process in [s3_process_files]:
        try:
            file_process(on_file)
        except Exception as e:
            print(e)
            continue

    for existed_table_name in existed_table_names:
        if not existed_table_name in file_table_names:
            drop_table(existed_table_name)
            print(existed_table_name, 'deleted')


def semantic_search(query: str, table_name: str):
    query_embedding = create_embedding(query).tobytes().hex()
    with db_connection.cursor() as cursor:
        cursor.execute(f'''
            SELECT content, v <*> X'{query_embedding}' AS similarity
            FROM {table_name}
            ORDER BY similarity USE INDEX (vector_index) DESC
            LIMIT 5
        ''')
        return cursor.fetchall()


main()

# print(semantic_search('query', 'table_name'))
