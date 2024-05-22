# PyRAG

A library that makes it easy to get started with RAG applications with SingleStore.

## Installation

To install the package run:

```sh
pip install pyrag
```

## Usage Example

### 1. Import the `PyRAG` class from the `pyrag` package

```py
from pyrag import PyRAG
```

### 2. Create a `PyRAG` instance

```py
pyrag = PyRAG(
    connection_url='DB_CONNECTION_URL',
    embedding_model_name='text-embedding-3-small',
    openai_api_key='OPENAI_API_KEY',
)
```

Note, you can also use HugginFace models. In this case you need to provide a `huggingfacehub_api_token`.

### 3. Provide a knowledge source in the form of a URL or S3 bucket

Supported file types: `csv`, `json`, `txt`, `pdf`

#### URL Knowledge Source

```py
pyrag.files.url.sync_file(url="URL", table_name='TABLE_NAME')
```

#### S3 Bucket Knowledge Source

```py
pyrag.files.s3(
    access_key_id='AWS_ACCESS_KEY_ID',
    secret_access_key='AWS_SECRET_ACCESS_KEY',
    bucket_name='AWS_BUCKET_NAME',
).sync_files(
    # This parameter is optional. If you want to use all files from the s3 bucket, remove this parameter.
    allowed_files=['file_name_1', 'file_name_2', 'file_name_3'],
    # This parameter is optional. Use it if you want to rename the table. By default, the table serializes the file name.
    table_names={'file_name_1': 'file_name_1'}
```

### 4. Create a chat instance and chat session

```py
chat = pyrag.chat.create(
    id=1,
    model_name='gpt-3.5-turbo',
    knowledge_sources=[{'table': 'file_name_1'}],
    store=True,
    store_messages_history=True
)

chat_session = chat.create_session(id=1)
```

### 5. Use the chat instance

```py
response = chat_session.send('PROMPT')
print(response)
```

Find more usage examples [here](https://github.com/singlestore-labs/pyrag/tree/main/examples)
