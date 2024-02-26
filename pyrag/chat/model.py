from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

openai_chat_model_names = ['gpt-3.5-turbo']
chat_model_names = [*openai_chat_model_names]


class ChatModel(ChatOpenAI):
    pass
