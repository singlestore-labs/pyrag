from os import environ
from typing import Any, Optional

openai_chat_model_names = [
    'gpt-4-0125-preview',
    'gpt-4-turbo-preview',
    'gpt-4-1106-preview',
    'gpt-4-vision-preview',
    'gpt-4-1106-vision-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-4-32k',
    'gpt-4-32k-0613'
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-instruct'
]


class ChatModel:
    def __call__(
        self,
        model_name: Optional[str] = None,
        model_kwargs: dict[str, Any] = {}
    ):
        from langchain_core.pydantic_v1 import SecretStr

        if model_name in openai_chat_model_names:
            from langchain_openai import ChatOpenAI
            model_kwargs['temperature'] = model_kwargs.get('temperature', 0.1)
            return ChatOpenAI(
                api_key=SecretStr(environ.get('PR_OPENAI_API_KEY', '')),
                model=model_name,
                **model_kwargs,
            )

        from langchain_community.llms import HuggingFaceEndpoint
        model_kwargs['temperature'] = model_kwargs.get('temperature', 0.1)
        return HuggingFaceEndpoint(
            huggingfacehub_api_token=environ.get('PR_HUGGINGFACEHUB_API_TOKEN', ''),
            repo_id=model_name or 'huggingfaceh4/zephyr-7b-alpha',
            **model_kwargs
        )
