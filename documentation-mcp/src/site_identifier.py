"""Identify relevant documentation sites for a user query."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Dict, List, Optional
from urllib.parse import urlparse

from duckduckgo_search import DDGS

from .settings import Config


@dataclass
class SiteCandidate:
    title: str
    url: str
    snippet: str
    confidence: float


class SiteIdentifier:
    """Uses search heuristics to discover documentation sites."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._patterns = config.sites.patterns
        self._exclusions = config.sites.excluded_domains

    def _matches_patterns(self, hostname: str) -> bool:
        if not self._patterns:
            return True
        return any(fnmatch(hostname, pattern) for pattern in self._patterns)

    def _is_excluded(self, hostname: str) -> bool:
        return any(fnmatch(hostname, pattern) for pattern in self._exclusions)

    def _score_result(self, url: str, title: str, snippet: str) -> float:
        score = 0.5
        hostname = urlparse(url).hostname or ""
        if self._matches_patterns(hostname):
            score += 0.3
        if any(keyword in title.lower() for keyword in ("doc", "guide", "reference")):
            score += 0.1
        if any(keyword in snippet.lower() for keyword in ("syntax", "api", "usage")):
            score += 0.1
        return min(score, 0.99)

    def _search(self, query: str, limit: int) -> List[SiteCandidate]:
        candidates: List[SiteCandidate] = []
        with DDGS() as ddgs:
            for idx, result in enumerate(ddgs.text(query, max_results=limit * 2)):
                url = result.get("href") or result.get("url")
                title = result.get("title", "")
                snippet = result.get("body", "")
                if not url:
                    continue
                hostname = urlparse(url).hostname or ""
                if self._is_excluded(hostname):
                    continue
                if not self._matches_patterns(hostname) and len(candidates) >= limit:
                    continue
                candidate = SiteCandidate(
                    title=title,
                    url=url,
                    snippet=snippet,
                    confidence=self._score_result(url, title, snippet),
                )
                candidates.append(candidate)
                if len(candidates) >= limit:
                    break
        return candidates

    async def identify(self, query: str, limit: int = 5, metadata: Optional[Dict[str, str]] = None) -> List[SiteCandidate]:
        """Identify candidate documentation sites using DuckDuckGo search."""

        enriched_query = query
        if metadata and metadata.get("language"):
            enriched_query += f" {metadata['language']}"
        enriched_query += " documentation"

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._search, enriched_query, limit)
