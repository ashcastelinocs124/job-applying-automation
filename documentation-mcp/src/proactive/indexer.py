"""Proactive indexing orchestrator for documentation."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..settings import Config
from ..site_identifier import SiteIdentifier
from ..web_scraper import ScrapedPage, WebScraper
from ..zoekt.indexer import ZoektIndexer
from ..point_list.builder import PointListBuilder, PointList
from .scheduler import BackgroundScheduler, TaskStatus

LOGGER = logging.getLogger(__name__)


@dataclass
class IndexingTask:
    """Represents an indexing task for a URL."""

    url: str
    topic: Optional[str] = None
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProactiveIndexer:
    """Orchestrates proactive indexing of documentation.

    Features:
    - Auto-indexes discovered documentation sites
    - Maintains index freshness with periodic re-indexing
    - Combines Zoekt code indexing with point list extraction
    - Background processing with progress tracking
    """

    def __init__(
        self,
        config: Config,
        *,
        identifier: SiteIdentifier,
        scraper: WebScraper,
    ) -> None:
        self.config = config
        self.settings = config.proactive
        self.identifier = identifier
        self.scraper = scraper

        # Initialize sub-components
        self.scheduler = BackgroundScheduler(config)
        self.zoekt_indexer = ZoektIndexer(config)
        self.point_list_builder = PointListBuilder(config)

        # Track indexed URLs
        self._indexed_urls: Dict[str, float] = {}  # url -> timestamp
        self._point_lists: Dict[str, PointList] = {}  # url -> point list
        self._pending_urls: Set[str] = set()
        self._reindex_task: Optional[asyncio.Task[None]] = None

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    async def start(self) -> None:
        """Start the proactive indexer."""
        if not self.enabled:
            LOGGER.info("Proactive indexer is disabled")
            return

        await self.scheduler.start()

        # Start periodic re-indexing if configured
        if self.settings.reindex_interval > 0:
            self._reindex_task = asyncio.create_task(self._reindex_loop())

        LOGGER.info("Proactive indexer started")

    async def stop(self) -> None:
        """Stop the proactive indexer."""
        # Cancel reindex task if running
        if self._reindex_task and not self._reindex_task.done():
            self._reindex_task.cancel()
            try:
                await self._reindex_task
            except asyncio.CancelledError:
                pass
            self._reindex_task = None

        await self.scheduler.stop()
        LOGGER.info("Proactive indexer stopped")

    async def _reindex_loop(self) -> None:
        """Periodically check and re-index stale content."""
        while True:
            await asyncio.sleep(self.settings.reindex_interval)

            if not self.enabled:
                break

            try:
                await self._check_stale_indexes()
            except Exception as exc:
                LOGGER.error("Re-index loop error: %s", exc)

    async def _check_stale_indexes(self) -> None:
        """Check for stale indexes and schedule re-indexing."""
        now = time.time()
        stale_urls: List[str] = []

        for url, timestamp in self._indexed_urls.items():
            age = now - timestamp
            if age > self.settings.reindex_interval:
                stale_urls.append(url)

        for url in stale_urls[:5]:  # Limit batch size
            await self.schedule_indexing(url, priority=5)

        if stale_urls:
            LOGGER.info("Scheduled %d stale URLs for re-indexing", len(stale_urls))

    async def schedule_indexing(
        self,
        url: str,
        topic: Optional[str] = None,
        priority: int = 0,
    ) -> str:
        """Schedule a URL for indexing.

        Returns the task ID for tracking.
        """
        if url in self._pending_urls:
            LOGGER.debug("URL already pending: %s", url)
            return ""

        self._pending_urls.add(url)

        async def index_task() -> Dict[str, Any]:
            try:
                return await self._index_url(url, topic)
            finally:
                self._pending_urls.discard(url)

        task_id = await self.scheduler.schedule(
            name=f"index:{url[:50]}",
            func=index_task,
            priority=priority,
            metadata={"url": url, "topic": topic},
        )

        return task_id

    async def _index_url(
        self,
        url: str,
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Index a single URL.

        Performs:
        1. Scrape the page
        2. Extract code blocks for Zoekt
        3. Build point list
        4. Store results
        """
        result: Dict[str, Any] = {
            "url": url,
            "status": "pending",
            "zoekt": None,
            "point_list": None,
        }

        # Scrape the page
        page = await self.scraper.scrape(url)
        if not page:
            result["status"] = "scrape_failed"
            LOGGER.warning("Failed to scrape %s", url)
            return result

        # Extract and index code blocks
        if self.config.zoekt.enabled:
            code_blocks = self.zoekt_indexer.extract_code_blocks(page)
            if code_blocks:
                zoekt_result = await self.zoekt_indexer.index_pages(
                    [page],
                    repo_name=self._url_to_repo_name(url),
                )
                result["zoekt"] = zoekt_result

        # Build point list
        points_count = 0
        if self.config.point_list.enabled:
            point_list = self.point_list_builder.build(page)
            self._point_lists[url] = point_list
            points_count = len(point_list.points)
            result["point_list"] = {
                "id": point_list.id,
                "points_count": points_count,
            }

        # Mark as indexed
        self._indexed_urls[url] = time.time()
        result["status"] = "completed"

        LOGGER.info(
            "Indexed %s: %d code blocks, %d points",
            url,
            result.get("zoekt", {}).get("blocks_extracted", 0)
            if result.get("zoekt")
            else 0,
            points_count,
        )

        return result

    @staticmethod
    def _url_to_repo_name(url: str) -> str:
        """Convert a URL to a repository name for Zoekt."""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        hostname = parsed.hostname or "unknown"
        path = parsed.path.strip("/").replace("/", "_")[:30]
        return f"{hostname}_{path}" if path else hostname

    async def index_topic(
        self,
        topic: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Discover and index documentation for a topic.

        Uses the site identifier to find relevant URLs,
        then schedules them for indexing.
        """
        if not self.enabled:
            return {"status": "disabled", "topic": topic}

        # Discover relevant sites
        candidates = await self.identifier.identify(topic, limit=limit)

        if not candidates:
            return {
                "status": "no_candidates",
                "topic": topic,
            }

        # Schedule indexing for each candidate
        task_ids: List[str] = []
        for idx, candidate in enumerate(candidates):
            task_id = await self.schedule_indexing(
                url=candidate.url,
                topic=topic,
                priority=idx,  # Earlier results get higher priority
            )
            if task_id:
                task_ids.append(task_id)

        return {
            "status": "scheduled",
            "topic": topic,
            "candidates": len(candidates),
            "task_ids": task_ids,
        }

    async def index_on_scrape(self, page: ScrapedPage) -> None:
        """Called when a page is scraped to trigger auto-indexing."""
        if not self.enabled or not self.settings.auto_index_on_scrape:
            return

        if page.url in self._indexed_urls:
            # Already indexed, check if stale
            age = time.time() - self._indexed_urls[page.url]
            if age < self.settings.reindex_interval:
                return

        await self.schedule_indexing(page.url, priority=1)

    def get_point_list(self, url: str) -> Optional[PointList]:
        """Get the point list for a URL if available."""
        return self._point_lists.get(url)

    def get_all_point_lists(self) -> List[PointList]:
        """Get all indexed point lists."""
        return list(self._point_lists.values())

    def is_indexed(self, url: str) -> bool:
        """Check if a URL has been indexed."""
        return url in self._indexed_urls

    def get_index_age(self, url: str) -> Optional[float]:
        """Get the age of an index in seconds."""
        timestamp = self._indexed_urls.get(url)
        if timestamp is None:
            return None
        return time.time() - timestamp

    def get_stats(self) -> Dict[str, Any]:
        """Get indexer statistics."""
        return {
            "enabled": self.enabled,
            "indexed_urls": len(self._indexed_urls),
            "point_lists": len(self._point_lists),
            "pending_urls": len(self._pending_urls),
            "scheduler": self.scheduler.get_stats(),
            "zoekt": self.zoekt_indexer.get_index_stats(),
            "point_list_builder": self.point_list_builder.get_stats(),
        }

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an indexing task."""
        task = self.scheduler.get_task(task_id)
        if task:
            return task.to_dict()
        return None
