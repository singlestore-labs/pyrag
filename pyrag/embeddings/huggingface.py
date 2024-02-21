from langchain_community.embeddings import HuggingFaceEmbeddings
from pyrag.embeddings.creator import EmbeddingsCreator


class HuggingFaceEmbeddingsCreator(EmbeddingsCreator):
    def __init__(self):
        super().__init__(HuggingFaceEmbeddings().embed_documents)
