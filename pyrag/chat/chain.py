from typing import Optional, Union
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain.memory import ConversationBufferMemory

from pyrag.db.database import Database

ChatModel = Union[Runnable[LanguageModelInput, str], Runnable[LanguageModelInput, BaseMessage]]


class ChatChain(LLMChain):
    def __init__(
        self,
        db: Database,
        model: ChatModel,
        chat_id: int,
        session_id: int,
        store: bool,
        messages_table_name: str,
        system_role: Optional[str] = None,
        include_context: bool = True,
    ):
        if store:
            from pyrag.chat.db_message_history import ChatDatabaseMessageHistory
            message_history = ChatDatabaseMessageHistory(
                db=db,
                chat_id=chat_id,
                session_id=session_id,
                messages_table_name=messages_table_name
            )
        else:
            from langchain.memory import ChatMessageHistory
            message_history = ChatMessageHistory()

        memory = ConversationBufferMemory(
            chat_memory=message_history,
            input_key='input',
            memory_key='chat_history',
            return_messages=True
        )

        messages: list = [
            ('system', system_role or 'You are a helpful assistant.'),
            MessagesPlaceholder(variable_name='chat_history'),
        ]

        if include_context:
            messages.append(('human', 'context: {context}'))

        messages.append(('human', 'input: {input}'))

        _prompt_template = ChatPromptTemplate.from_messages(messages)

        super().__init__(
            llm=model,
            memory=memory,
            prompt=_prompt_template,
        )
