"""Recursive exploration of documentation topics."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .settings import Config
from .site_identifier import SiteIdentifier
from .web_scraper import WebScraper

LOGGER = logging.getLogger(__name__)


@dataclass
class ExplorationNode:
    url: str
    title: str
    summary: str
    links: List[str]
    depth: int


class DeepSearchOrchestrator:
    """Coordinates deep crawling of documentation starting from a query."""

    def __init__(self, config: Config, identifier: SiteIdentifier, scraper: WebScraper) -> None:
        self.config = config
        self.identifier = identifier
        self.scraper = scraper
        self.max_depth = 3
        self.max_nodes = 20

    async def _summarize_page(self, url: str) -> Optional[ExplorationNode]:
        page = await self.scraper.scrape(url)
        if not page:
            return None
        summary = page.text[:4000]
        return ExplorationNode(
            url=url,
            title=page.title,
            summary=summary,
            links=page.links[:20],
            depth=0,
        )

    async def explore(self, topic: str, depth: int = 1, limit: int = 5) -> Dict[str, List[Dict[str, str]]]:
        depth = max(1, min(depth, self.max_depth))
        limit = max(1, min(limit, self.max_nodes))

        candidates = await self.identifier.identify(topic, limit=limit)
        visited: Set[str] = set()
        results: List[Dict[str, str]] = []

        queue: List[ExplorationNode] = []
        initial_tasks = [self._summarize_page(candidate.url) for candidate in candidates]
        initial_pages = await asyncio.gather(*initial_tasks)
        for node in initial_pages:
            if node is None or node.url in visited:
                continue
            node.depth = 0
            visited.add(node.url)
            queue.append(node)

        while queue:
            node = queue.pop(0)
            results.append(
                {
                    "url": node.url,
                    "title": node.title,
                    "summary": node.summary,
                    "depth": node.depth,
                    "links": node.links,
                }
            )
            if len(results) >= limit or node.depth + 1 >= depth:
                continue

            next_links = [link for link in node.links if link not in visited]
            tasks = [self._summarize_page(link) for link in next_links[:5]]
            pages = await asyncio.gather(*tasks)
            for child in pages:
                if child is None or child.url in visited:
                    continue
                child.depth = node.depth + 1
                visited.add(child.url)
                queue.append(child)
                if len(results) + len(queue) >= limit:
                    break

        return {
            "topic": topic,
            "results": results,
        }
