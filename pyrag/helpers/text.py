from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter


def split(text: str, separator="\n\n", chunk_size=1024, chunk_overlap=126, *args, **kwargs):
    return CharacterTextSplitter(
        separator=separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        *args,
        **kwargs
    ).split_text(text)


def split_recursively(text: str, chunk_size=1024, chunk_overlap=126, *args, **kwargs):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        *args,
        **kwargs
    ).split_text(text)


def split_by_tokens(text: str, encoding="cl100k_base", chunk_size=1024, chunk_overlap=0, *args, **kwargs):
    return CharacterTextSplitter.from_tiktoken_encoder(
        encoding=encoding,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        *args,
        **kwargs
    ).split_text(text)
