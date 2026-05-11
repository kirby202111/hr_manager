from __future__ import annotations

from openai import OpenAI

from app.config import settings

_client = OpenAI(
    api_key=settings.dashscope_api_key,
    base_url=settings.dashscope_base_url,
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = _client.embeddings.create(
        model=settings.dashscope_embedding_model,
        input=texts,
    )
    data = sorted(response.data, key=lambda d: d.index)
    return [d.embedding for d in data]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
