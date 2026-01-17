"""Unified search engine combining Zoekt and point list results."""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .settings import Config
from .zoekt.search import ZoektSearchEngine, CodeSearchResult
from .point_list.builder import PointListBuilder, PointList
from .point_list.analyzer import ExtractedPoint, PointType
from .point_list.knowledge import KnowledgeGraph
from .proactive.indexer import ProactiveIndexer
from .web_scraper import ScrapedPage

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiedSearchResult:
    """A unified search result combining multiple sources."""

    query: str
    code_results: List[CodeSearchResult] = field(default_factory=list)
    point_results: List[ExtractedPoint] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    natural_response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "query": self.query,
            "code_results": [
                {
                    "file_path": r.file_path,
                    "language": r.language,
                    "snippet": r.snippet,
                    "line_number": r.line_number,
                    "context": r.context,
                    "score": r.score,
                    "source_url": r.source_url,
                }
                for r in self.code_results
            ],
            "point_results": [
                {
                    "id": p.id,
                    "type": p.point_type.name,
                    "name": p.name,
                    "description": p.description,
                    "confidence": p.confidence,
                }
                for p in self.point_results
            ],
            "sources": self.sources,
            "natural_response": self.natural_response,
            "metadata": self.metadata,
        }


class EnhancedSearchEngine:
    """Unified search combining Zoekt code search with point list knowledge.

    Features:
    - Instant code search via Zoekt
    - Concept/function search via point lists
    - Knowledge graph traversal for related results
    - Natural language response generation
    """

    def __init__(
        self,
        config: Config,
        *,
        proactive_indexer: Optional[ProactiveIndexer] = None,
    ) -> None:
        self.config = config
        self.zoekt_engine = ZoektSearchEngine(config)
        self.point_list_builder = PointListBuilder(config)
        self.knowledge_graph = KnowledgeGraph(config)
        self.proactive_indexer = proactive_indexer
        self._llm_client = self._init_llm_client()

    def _init_llm_client(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if OpenAI is None or not api_key:
            LOGGER.info("OpenAI unavailable; natural language responses disabled")
            return None
        try:
            return OpenAI(api_key=api_key)
        except Exception as exc:
            LOGGER.warning("Failed to init OpenAI client: %s", exc)
            return None

    async def close(self) -> None:
        """Clean up resources."""
        await self.zoekt_engine.close()

    async def __aenter__(self) -> "EnhancedSearchEngine":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    async def search(
        self,
        query: str,
        *,
        include_code: bool = True,
        include_points: bool = True,
        include_related: bool = True,
        generate_response: bool = True,
        max_results: int = 10,
        language: Optional[str] = None,
    ) -> UnifiedSearchResult:
        """Perform a unified search across all sources.

        Args:
            query: The search query
            include_code: Search Zoekt for code matches
            include_points: Search point lists for concepts/functions
            include_related: Include related points from knowledge graph
            generate_response: Generate natural language response
            max_results: Maximum results per source
            language: Optional language filter for code

        Returns:
            UnifiedSearchResult with combined results
        """
        result = UnifiedSearchResult(query=query)
        sources: set = set()

        # Parallel search across sources
        tasks: List[asyncio.Task[Any]] = []

        if include_code and self.zoekt_engine.enabled:
            tasks.append(
                asyncio.create_task(
                    self.zoekt_engine.search(
                        query,
                        language=language,
                        max_results=max_results,
                    )
                )
            )
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Placeholder

        if include_points:
            tasks.append(asyncio.create_task(self._search_points(query, max_results)))
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Placeholder

        # Wait for all searches
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process code results
        code_res = results[0]
        if include_code and not isinstance(code_res, BaseException) and code_res:
            result.code_results = [
                r for r in code_res if isinstance(r, CodeSearchResult)
            ]
            for r in result.code_results:
                if r.source_url:
                    sources.add(r.source_url)

        # Process point results
        point_res = results[1]
        if include_points and not isinstance(point_res, BaseException) and point_res:
            result.point_results = [
                p for p in point_res if isinstance(p, ExtractedPoint)
            ]
            for p in result.point_results:
                sources.add(p.source_url)

        # Expand with related points from knowledge graph
        if include_related and result.point_results:
            related = self._get_related_points(result.point_results[:3])
            # Add related points not already in results
            existing_ids = {p.id for p in result.point_results}
            for point in related:
                if point.id not in existing_ids:
                    result.point_results.append(point)
                    sources.add(point.source_url)

        result.sources = list(sources)

        # Generate natural language response
        if generate_response and (result.code_results or result.point_results):
            result.natural_response = await self._generate_response(
                query,
                result.code_results[:5],
                result.point_results[:5],
            )

        result.metadata = {
            "code_count": len(result.code_results),
            "point_count": len(result.point_results),
            "source_count": len(result.sources),
        }

        return result

    async def _search_points(
        self,
        query: str,
        limit: int,
    ) -> List[ExtractedPoint]:
        """Search across all point lists."""
        all_points: List[ExtractedPoint] = []

        # Search in knowledge graph first (includes related points)
        graph_results = self.knowledge_graph.search(query, limit=limit)
        all_points.extend(graph_results)

        # Also search in proactive indexer's point lists
        if self.proactive_indexer:
            for point_list in self.proactive_indexer.get_all_point_lists():
                matches = point_list.search(query, limit=limit)
                for point in matches:
                    if point.id not in {p.id for p in all_points}:
                        all_points.append(point)

        # Sort by confidence and limit
        all_points.sort(key=lambda p: p.confidence, reverse=True)
        return all_points[:limit]

    def _get_related_points(
        self,
        points: List[ExtractedPoint],
    ) -> List[ExtractedPoint]:
        """Get related points from knowledge graph."""
        related: List[ExtractedPoint] = []

        for point in points:
            point_related = self.knowledge_graph.get_related(point.id)
            for r in point_related:
                if r.id not in {p.id for p in related}:
                    related.append(r)

        return related[:5]

    async def _generate_response(
        self,
        query: str,
        code_results: List[CodeSearchResult],
        point_results: List[ExtractedPoint],
    ) -> str:
        """Generate a natural language response from search results."""
        if self._llm_client is None:
            return self._fallback_response(code_results, point_results)

        # Build context from results
        context_parts: List[str] = []

        if point_results:
            context_parts.append("## Concepts and Functions")
            for point in point_results:
                context_parts.append(
                    f"- **{point.name}** ({point.point_type.name}): {point.description}"
                )

        if code_results:
            context_parts.append("\n## Code Examples")
            for result in code_results:
                context_parts.append(
                    f"```{result.language}\n{result.snippet}\n```"
                    f"\n_From: {result.source_url or result.file_path}_"
                )

        context = "\n".join(context_parts)

        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=self.config.ai.temperature,
                max_tokens=self.config.ai.max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a documentation assistant. Use the provided context "
                            "to answer the user's question concisely. Include code examples "
                            "when relevant. Cite sources."
                        ),
                    },
                    {"role": "user", "content": f"Context:\n{context}"},
                    {"role": "user", "content": f"Question: {query}"},
                ],
            )
            content = response.choices[0].message.content
            return (
                content.strip()
                if content
                else self._fallback_response(code_results, point_results)
            )
        except Exception as exc:
            LOGGER.warning("LLM generation failed: %s", exc)
            return self._fallback_response(code_results, point_results)

    @staticmethod
    def _fallback_response(
        code_results: List[CodeSearchResult],
        point_results: List[ExtractedPoint],
    ) -> str:
        """Generate a simple response without LLM."""
        lines: List[str] = []

        if point_results:
            lines.append("**Key Findings:**")
            for point in point_results[:3]:
                lines.append(f"- {point.name}: {point.description[:100]}...")

        if code_results:
            lines.append("\n**Code Examples:**")
            for result in code_results[:2]:
                lines.append(f"```{result.language}")
                lines.append(result.snippet[:200])
                lines.append("```")

        return "\n".join(lines) if lines else "No relevant results found."

    async def search_code(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 10,
    ) -> List[CodeSearchResult]:
        """Search for code only."""
        return await self.zoekt_engine.search(
            query,
            language=language,
            max_results=limit,
        )

    async def search_concepts(
        self,
        query: str,
        limit: int = 10,
    ) -> List[ExtractedPoint]:
        """Search for concepts/functions only."""
        return await self._search_points(query, limit)

    async def find_examples(
        self,
        topic: str,
        language: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find code examples for a topic."""
        return await self.zoekt_engine.search_examples(
            topic,
            language=language,
            limit=limit,
        )

    def build_knowledge_from_pages(
        self,
        pages: List[ScrapedPage],
    ) -> None:
        """Build knowledge graph from scraped pages."""
        for page in pages:
            point_list = self.point_list_builder.build(page)
            self.knowledge_graph.from_point_list(point_list)

        LOGGER.info(
            "Built knowledge graph: %d nodes, %d edges",
            self.knowledge_graph.node_count,
            self.knowledge_graph.edge_count,
        )

    async def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        zoekt_stats = await self.zoekt_engine.get_stats()
        return {
            "zoekt": zoekt_stats,
            "point_list_builder": self.point_list_builder.get_stats(),
            "knowledge_graph": self.knowledge_graph.get_stats(),
            "llm_available": self._llm_client is not None,
        }
