from typing import Optional, Union
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import LanguageModelInput
from langchain_core.memory import BaseMemory
from langchain_core.messages import BaseMessage
from langchain_core.prompts.chat import BaseChatPromptTemplate
from langchain_core.runnables import Runnable

ChatChainModel = Union[Runnable[LanguageModelInput, str], Runnable[LanguageModelInput, BaseMessage]]


class ChatChain(LLMChain):
    def __init__(
        self,
        model: ChatChainModel,
        memory: Optional[BaseMemory] = None,
        system_role: Optional[str] = None,
        prompt_tempalate: Optional[BaseChatPromptTemplate] = None,
        *args,
        **kwargs
    ):
        _prompt_template = prompt_tempalate or ChatPromptTemplate.from_messages([
            ("system", system_role or 'You are a helpful assistant'),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        super().__init__(
            llm=model,
            memory=memory,
            prompt=_prompt_template,
            *args,
            **kwargs
        )
