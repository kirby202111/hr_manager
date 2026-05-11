from __future__ import annotations

from dataclasses import dataclass

from app.config import settings


@dataclass
class Chunk:
    text: str
    index: int
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    cs = chunk_size or settings.knowledge_base_chunk_size
    ov = overlap or settings.knowledge_base_chunk_overlap
    stride = cs - ov

    if stride <= 0:
        raise ValueError("chunk_size must be greater than chunk_overlap")

    chunks: list[Chunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + cs, len(text))

        # 尝试在重叠区域内按换行符断开
        if end < len(text):
            search_start = max(end - ov, start)
            last_nl = text.rfind("\n", search_start, end)
            if last_nl > start:
                end = last_nl

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(Chunk(text=chunk, index=idx, start_char=start, end_char=end))
            idx += 1

        start = start + stride if end - start == cs else end

    return chunks
