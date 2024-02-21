from langchain_community.embeddings import HuggingFaceEmbeddings as _HuggingFaceEmbeddings
from pyrag.embeddings.creator import EmbeddingsCreator


class HuggingFaceEmbeddings(EmbeddingsCreator):
    def __init__(self):
        super().__init__(_HuggingFaceEmbeddings().embed_documents)
