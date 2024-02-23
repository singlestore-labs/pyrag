from pyrag.embeddings.base import BaseEmbeddings


class HuggingFaceEmbeddings(BaseEmbeddings):
    def __init__(self):
        from langchain_community.embeddings import HuggingFaceEmbeddings
        super().__init__(HuggingFaceEmbeddings().embed_documents)
