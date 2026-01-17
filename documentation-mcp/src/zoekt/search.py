"""Search interface for Zoekt integration."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..settings import Config
from .client import ZoektClient, ZoektResult, ZoektMatch, ZoektError

LOGGER = logging.getLogger(__name__)


@dataclass
class CodeSearchResult:
    """A unified code search result."""

    file_path: str
    repository: str
    language: str
    snippet: str
    line_number: int
    context: str
    score: float
    source_url: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


class ZoektSearchEngine:
    """High-level search interface combining Zoekt with metadata enrichment."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = ZoektClient(config)

    @property
    def enabled(self) -> bool:
        return self.client.enabled

    async def close(self) -> None:
        await self.client.close()

    async def __aenter__(self) -> "ZoektSearchEngine":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    def _extract_source_url(self, file_path: str, content: str) -> Optional[str]:
        """Extract source URL from metadata header in indexed file."""
        for line in content.split("\n")[:5]:
            if line.startswith("# Source:"):
                return line.replace("# Source:", "").strip()
        return None

    def _build_context(self, match: ZoektMatch) -> str:
        """Build context string from match with before/after lines."""
        lines: List[str] = []

        for line in match.context_before:
            lines.append(f"  {line}")

        lines.append(f"> {match.line_content}")

        for line in match.context_after:
            lines.append(f"  {line}")

        return "\n".join(lines)

    def _convert_result(self, result: ZoektResult) -> List[CodeSearchResult]:
        """Convert a ZoektResult to CodeSearchResult objects."""
        code_results: List[CodeSearchResult] = []

        for match in result.matches:
            context = self._build_context(match)
            source_url = self._extract_source_url(
                result.file_name,
                match.line_content,
            )

            code_results.append(
                CodeSearchResult(
                    file_path=result.file_name,
                    repository=result.repository,
                    language=result.language,
                    snippet=match.line_content,
                    line_number=match.line_number,
                    context=context,
                    score=result.score,
                    source_url=source_url,
                )
            )

        return code_results

    async def search(
        self,
        query: str,
        *,
        language: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> List[CodeSearchResult]:
        """Search for code matching the query.

        Args:
            query: The search query (natural language or code pattern)
            language: Optional language filter
            max_results: Maximum number of results

        Returns:
            List of CodeSearchResult objects
        """
        if not self.enabled:
            return []

        try:
            results = await self.client.search_code(
                query,
                language=language,
                file_pattern=None,
            )

            code_results: List[CodeSearchResult] = []
            for result in results:
                code_results.extend(self._convert_result(result))

            if max_results:
                code_results = code_results[:max_results]

            return code_results

        except ZoektError as exc:
            LOGGER.warning("Zoekt search failed: %s", exc)
            return []

    async def search_examples(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for code examples matching the query.

        Returns simplified results suitable for example retrieval.
        """
        results = await self.search(query, language=language, max_results=limit * 2)

        examples: List[Dict[str, Any]] = []
        seen_snippets: set = set()

        for result in results:
            # Deduplicate similar snippets
            snippet_key = result.snippet.strip()[:100]
            if snippet_key in seen_snippets:
                continue
            seen_snippets.add(snippet_key)

            examples.append(
                {
                    "code": result.snippet,
                    "language": result.language,
                    "context": result.context,
                    "source_url": result.source_url,
                    "score": result.score,
                }
            )

            if len(examples) >= limit:
                break

        return examples

    async def find_similar_code(
        self,
        code_snippet: str,
        language: Optional[str] = None,
    ) -> List[CodeSearchResult]:
        """Find code similar to the provided snippet.

        Extracts key identifiers from the snippet and searches for them.
        """
        # Extract potential identifiers (function names, variables, etc.)
        identifiers = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]{2,})\b", code_snippet)

        # Filter common keywords
        keywords = {
            "def",
            "class",
            "import",
            "from",
            "return",
            "if",
            "else",
            "for",
            "while",
            "try",
            "except",
            "with",
            "as",
            "in",
            "not",
            "and",
            "or",
            "True",
            "False",
            "None",
            "self",
            "function",
            "const",
            "let",
            "var",
            "async",
            "await",
            "export",
            "default",
            "this",
            "new",
        }
        identifiers = [i for i in identifiers if i not in keywords]

        if not identifiers:
            return []

        # Search for the most distinctive identifiers
        query = " ".join(identifiers[:5])
        return await self.search(query, language=language, max_results=10)

    async def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        if not self.enabled:
            return {"enabled": False}

        repos = await self.client.list_repos()
        healthy = await self.client.health_check()

        return {
            "enabled": True,
            "healthy": healthy,
            "server_url": self.config.zoekt.server_url,
            "indexed_repos": len(repos),
            "repos": [r.get("Name", "unknown") for r in repos[:10]],
        }
