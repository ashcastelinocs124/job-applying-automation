"""Async HTTP client for Zoekt search server API."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientError, ClientSession

from ..settings import Config

LOGGER = logging.getLogger(__name__)


class ZoektError(Exception):
    """Raised when Zoekt API operations fail."""


@dataclass
class ZoektMatch:
    """A single match within a file."""

    line_number: int
    line_content: str
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)


@dataclass
class ZoektResult:
    """A search result from Zoekt."""

    file_name: str
    repository: str
    language: str
    matches: List[ZoektMatch] = field(default_factory=list)
    score: float = 0.0


class ZoektClient:
    """Async client for Zoekt webserver JSON API.

    Zoekt provides a REST API at /search endpoint that accepts:
    - q: query string
    - num: max results
    - ctx: context lines around matches
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.settings = config.zoekt
        self._session: Optional[ClientSession] = None

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    async def _get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.settings.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "ZoektClient":
        await self._get_session()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    async def health_check(self) -> bool:
        """Check if Zoekt server is reachable."""
        if not self.enabled:
            return False

        try:
            session = await self._get_session()
            async with session.get(f"{self.settings.server_url}/") as response:
                return response.status == 200
        except ClientError as exc:
            LOGGER.warning("Zoekt health check failed: %s", exc)
            return False

    async def search(
        self,
        query: str,
        *,
        max_results: Optional[int] = None,
        context_lines: Optional[int] = None,
        repos: Optional[List[str]] = None,
    ) -> List[ZoektResult]:
        """Execute a search query against Zoekt.

        Args:
            query: The search query (supports regex, file filters, etc.)
            max_results: Maximum number of results to return
            context_lines: Lines of context around each match
            repos: Optional list of repositories to search in

        Returns:
            List of ZoektResult objects with matches
        """
        if not self.enabled:
            LOGGER.debug("Zoekt is disabled, returning empty results")
            return []

        max_results = max_results or self.settings.max_results
        context_lines = context_lines or self.settings.context_lines

        params: Dict[str, Any] = {
            "q": query,
            "num": max_results,
            "ctx": context_lines,
        }

        if repos:
            # Zoekt uses r: prefix for repo filter
            repo_filter = " OR ".join(f"r:{repo}" for repo in repos)
            params["q"] = f"({query}) ({repo_filter})"

        try:
            session = await self._get_session()
            url = f"{self.settings.server_url}/search"

            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_results(data)

        except ClientError as exc:
            LOGGER.error("Zoekt search failed: %s", exc)
            raise ZoektError(f"Search request failed: {exc}") from exc
        except Exception as exc:
            LOGGER.error("Unexpected error during Zoekt search: %s", exc)
            raise ZoektError(f"Search failed: {exc}") from exc

    def _parse_results(self, data: Dict[str, Any]) -> List[ZoektResult]:
        """Parse Zoekt JSON response into result objects."""
        results: List[ZoektResult] = []

        file_matches = data.get("Result", {}).get("FileMatches") or []

        for file_match in file_matches:
            file_name = file_match.get("FileName", "")
            repository = file_match.get("Repository", "")
            language = file_match.get("Language", "")
            score = float(file_match.get("Score", 0.0))

            matches: List[ZoektMatch] = []
            line_matches = file_match.get("LineMatches") or []

            for line_match in line_matches:
                line_number = line_match.get("LineNumber", 0)
                line_content = line_match.get("Line", "")

                # Handle context if provided
                before = line_match.get("Before") or []
                after = line_match.get("After") or []

                matches.append(
                    ZoektMatch(
                        line_number=line_number,
                        line_content=line_content,
                        context_before=before,
                        context_after=after,
                    )
                )

            results.append(
                ZoektResult(
                    file_name=file_name,
                    repository=repository,
                    language=language,
                    matches=matches,
                    score=score,
                )
            )

        return results

    async def list_repos(self) -> List[Dict[str, Any]]:
        """List all indexed repositories."""
        if not self.enabled:
            return []

        try:
            session = await self._get_session()
            url = f"{self.settings.server_url}/api/list"

            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("Repos", [])

        except ClientError as exc:
            LOGGER.warning("Failed to list Zoekt repos: %s", exc)
            return []

    async def search_code(
        self,
        query: str,
        language: Optional[str] = None,
        file_pattern: Optional[str] = None,
    ) -> List[ZoektResult]:
        """Search for code with optional language and file filters.

        This is a convenience wrapper around search() that builds
        appropriate Zoekt query syntax.
        """
        filters: List[str] = []

        if language:
            filters.append(f"lang:{language}")

        if file_pattern:
            filters.append(f"f:{file_pattern}")

        full_query = query
        if filters:
            full_query = f"{query} {' '.join(filters)}"

        return await self.search(full_query)
