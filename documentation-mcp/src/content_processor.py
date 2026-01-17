"""Process scraped documentation into RAG-friendly chunks."""
from __future__ import annotations

import itertools
import math
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from sentence_transformers import SentenceTransformer

from .settings import Config


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: Dict[str, str]
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DocumentChunk":
        return cls(
            chunk_id=payload.get("chunk_id", ""),
            text=payload.get("text", ""),
            metadata=payload.get("metadata", {}) or {},
            embedding=payload.get("embedding"),
        )


class ContentProcessor:
    """Chunks and embeds documentation for semantic retrieval."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.model = SentenceTransformer(config.rag.embedding_model)
        self.chunk_size = config.rag.chunk_size
        self.chunk_overlap = config.rag.chunk_overlap

    def chunk_text(self, text: str, metadata: Optional[Dict[str, str]] = None) -> List[DocumentChunk]:
        metadata = metadata or {}
        words = text.split()
        if not words:
            return []

        step = max(self.chunk_size - self.chunk_overlap, 1)
        chunks: List[DocumentChunk] = []
        for start in range(0, len(words), step):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            if not chunk_words:
                continue
            chunk_text = " ".join(chunk_words)
            chunk_metadata = dict(metadata)
            chunk_metadata.update(
                {
                    "chunk_index": str(len(chunks)),
                    "start_word": str(start),
                    "end_word": str(end),
                }
            )
            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    text=chunk_text,
                    metadata=chunk_metadata,
                )
            )
            if end >= len(words):
                break
        return chunks

    def embed_chunks(self, chunks: Iterable[DocumentChunk]) -> List[DocumentChunk]:
        chunk_list = list(chunks)
        if not chunk_list:
            return []
        texts = [chunk.text for chunk in chunk_list]
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=False)
        for chunk, embedding in zip(chunk_list, embeddings):
            chunk.embedding = embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
        return chunk_list

    def process_document(self, text: str, metadata: Optional[Dict[str, str]] = None) -> List[DocumentChunk]:
        chunks = self.chunk_text(text, metadata)
        return self.embed_chunks(chunks)
