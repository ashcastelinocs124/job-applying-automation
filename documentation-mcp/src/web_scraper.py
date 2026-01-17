"""Asynchronous web scraping utilities for documentation sites."""
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from aiohttp import ClientError, ClientSession
from bs4 import BeautifulSoup
from markdownify import markdownify
from readability import Document

from .settings import Config

LOGGER = logging.getLogger(__name__)


@dataclass
class ScrapedPage:
    url: str
    title: str
    html: str
    text: str
    markdown: str
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class WebScraper:
    """Fetches and normalizes documentation pages."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._semaphore = asyncio.Semaphore(config.scraping.max_concurrent_requests)
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.scraping.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "WebScraper":
        await self._get_session()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch raw HTML for a URL with throttling and retries."""

        async with self._semaphore:
            session = await self._get_session()
            headers = {"User-Agent": self.config.scraping.user_agent}
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    html = await response.text()
                    await asyncio.sleep(self.config.scraping.request_delay)
                    return html
            except ClientError as exc:
                LOGGER.warning("Failed to fetch %s: %s", url, exc)
                return None

    @staticmethod
    def _extract_links(url: str, soup: BeautifulSoup) -> List[str]:
        links: List[str] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if href.startswith("#"):
                continue
            absolute = urljoin(url, href)
            parsed = urlparse(absolute)
            if parsed.scheme.startswith("http"):
                links.append(absolute)
        return list(dict.fromkeys(links))  # Preserve order, remove duplicates

    @staticmethod
    def _cleanup_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _parse(self, url: str, html: str) -> ScrapedPage:
        doc = Document(html)
        summary_html = doc.summary() or html
        title = doc.short_title() or url

        soup = BeautifulSoup(summary_html, "lxml")
        text = soup.get_text("\n")
        markdown = markdownify(summary_html, heading_style="ATX")
        links = self._extract_links(url, soup)

        return ScrapedPage(
            url=url,
            title=title,
            html=summary_html,
            text=self._cleanup_text(text),
            markdown=markdown,
            links=links,
            metadata={"source_title": title},
        )

    async def scrape(self, url: str) -> Optional[ScrapedPage]:
        """Fetch and normalize a documentation page."""

        html = await self.fetch(url)
        if not html:
            return None
        return self._parse(url, html)

    async def scrape_many(self, urls: List[str]) -> List[ScrapedPage]:
        tasks = [self.scrape(url) for url in urls]
        pages = await asyncio.gather(*tasks, return_exceptions=True)
        results: List[ScrapedPage] = []
        for page in pages:
            if isinstance(page, Exception):
                LOGGER.warning("Scrape task failed: %s", page)
                continue
            if page is not None:
                results.append(page)
        return results
