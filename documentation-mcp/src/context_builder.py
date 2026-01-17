"""Context assembly utilities for documentation responses."""
from __future__ import annotations

from typing import Dict, List


class ContextBuilder:
    """Formats chunks and metadata into MCP-friendly responses."""

    @staticmethod
    def format_sources(top_chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        sources: List[Dict[str, str]] = []
        for chunk in top_chunks:
            sources.append(
                {
                    "title": chunk["site"].get("title", ""),
                    "url": chunk["site"].get("url", ""),
                    "confidence": chunk["site"].get("confidence", 0),
                    "score": chunk.get("score", 0),
                }
            )
        return sources

    @staticmethod
    def build_response(query: str, answer: str, top_chunks: List[Dict[str, str]]) -> Dict[str, object]:
        return {
            "query": query,
            "answer": answer,
            "sources": ContextBuilder.format_sources(top_chunks),
            "chunks": top_chunks,
        }
