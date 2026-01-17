"""Documentation loading with multiple input methods: file upload, URL, or name search."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import tempfile
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .settings import Config
from .site_identifier import SiteCandidate, SiteIdentifier
from .web_scraper import ScrapedPage, WebScraper

LOGGER = logging.getLogger(__name__)


class LoadMethod(Enum):
    """How the documentation was loaded."""
    
    FILE_UPLOAD = auto()
    URL = auto()
    NAME_SEARCH = auto()


@dataclass
class LoadedDocumentation:
    """Result of loading documentation."""
    
    method: LoadMethod
    pages: List[ScrapedPage]
    source: str  # Original input (file path, URL, or name)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def page_count(self) -> int:
        return len(self.pages)
    
    @property
    def total_content_length(self) -> int:
        return sum(len(p.markdown or p.text) for p in self.pages)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method.name,
            "source": self.source,
            "page_count": self.page_count,
            "total_content_length": self.total_content_length,
            "pages": [
                {
                    "url": p.url,
                    "title": p.title,
                    "content_length": len(p.markdown or p.text),
                }
                for p in self.pages
            ],
            "metadata": self.metadata,
        }


class DocumentationFinder:
    """AI-powered agent to find documentation by name."""
    
    def __init__(self, config: Config, site_identifier: SiteIdentifier) -> None:
        self.config = config
        self.site_identifier = site_identifier
        self._llm_client = self._init_llm_client()
    
    def _init_llm_client(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if OpenAI is None or not api_key:
            LOGGER.info("OpenAI unavailable; using basic search for documentation discovery")
            return None
        try:
            return OpenAI(api_key=api_key)
        except Exception as exc:
            LOGGER.warning("Failed to initialize OpenAI: %s", exc)
            return None
    
    async def find_documentation(
        self,
        name: str,
        max_results: int = 5,
    ) -> List[SiteCandidate]:
        """Find documentation sites by library/framework name."""
        
        # Step 1: Use AI to generate optimal search queries
        search_queries = await self._generate_search_queries(name)
        
        # Step 2: Search for each query and collect candidates
        all_candidates: List[SiteCandidate] = []
        seen_urls = set()
        
        for query in search_queries:
            candidates = await self.site_identifier.identify(query, limit=max_results)
            for candidate in candidates:
                if candidate.url not in seen_urls:
                    seen_urls.add(candidate.url)
                    all_candidates.append(candidate)
        
        # Step 3: Use AI to rank and select best documentation sites
        ranked_candidates = await self._rank_candidates(name, all_candidates)
        
        return ranked_candidates[:max_results]
    
    async def _generate_search_queries(self, name: str) -> List[str]:
        """Generate search queries to find documentation."""
        
        # Default queries
        default_queries = [
            f"{name} official documentation",
            f"{name} docs",
            f"{name} API reference",
            f"{name} getting started guide",
        ]
        
        if not self._llm_client:
            return default_queries
        
        prompt = f"""
        Generate 4 search queries to find the official documentation for: "{name}"
        
        Consider:
        - Official documentation sites
        - GitHub repositories with docs
        - ReadTheDocs or similar platforms
        - API references
        
        Return a JSON array of search query strings.
        Example: ["react official documentation", "react docs", "reactjs.org", "react API reference"]
        """
        
        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=0.3,
                max_tokens=200,
                messages=[
                    {"role": "system", "content": "You are a documentation search expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            queries = json.loads(response.choices[0].message.content)
            return queries if isinstance(queries, list) else default_queries
            
        except Exception as exc:
            LOGGER.warning("AI query generation failed: %s", exc)
            return default_queries
    
    async def _rank_candidates(
        self,
        name: str,
        candidates: List[SiteCandidate],
    ) -> List[SiteCandidate]:
        """Rank candidates by relevance to the documentation name."""
        
        if not candidates:
            return []
        
        if not self._llm_client:
            # Simple heuristic ranking
            return self._heuristic_rank(name, candidates)
        
        # Prepare candidates for AI ranking
        candidate_summaries = []
        for i, c in enumerate(candidates[:15]):  # Limit to avoid token issues
            summary = f"{i+1}. {c.title} - {c.url}\n   {c.snippet[:100]}..."
            candidate_summaries.append(summary)
        
        prompt = f"""
        Rank these documentation site candidates for "{name}" by relevance.
        
        Candidates:
        {chr(10).join(candidate_summaries)}
        
        Return a JSON array of indices (0-based) ordered by relevance, best first.
        Prefer official documentation, then well-maintained community docs.
        
        Example response: [2, 0, 5, 1, 3]
        """
        
        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=0.1,
                max_tokens=100,
                messages=[
                    {"role": "system", "content": "You are a documentation relevance expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            indices = json.loads(response.choices[0].message.content)
            
            ranked = []
            for idx in indices:
                if 0 <= idx < len(candidates):
                    ranked.append(candidates[idx])
            
            # Add any remaining candidates not in the ranking
            for c in candidates:
                if c not in ranked:
                    ranked.append(c)
            
            return ranked
            
        except Exception as exc:
            LOGGER.warning("AI ranking failed: %s", exc)
            return self._heuristic_rank(name, candidates)
    
    def _heuristic_rank(self, name: str, candidates: List[SiteCandidate]) -> List[SiteCandidate]:
        """Rank candidates using heuristics."""
        name_lower = name.lower()
        
        def score(c: SiteCandidate) -> float:
            s = c.confidence
            url_lower = c.url.lower()
            title_lower = c.title.lower()
            
            # Boost for name in URL
            if name_lower in url_lower:
                s += 0.3
            
            # Boost for official-looking URLs
            if any(x in url_lower for x in [".io", ".dev", ".org", "github.com"]):
                s += 0.1
            
            # Boost for "docs" or "documentation" in URL/title
            if "docs" in url_lower or "documentation" in title_lower:
                s += 0.2
            
            # Boost for "official" in title
            if "official" in title_lower:
                s += 0.2
            
            return s
        
        return sorted(candidates, key=score, reverse=True)


class DocumentationLoader:
    """Unified loader for documentation from multiple sources."""
    
    def __init__(
        self,
        config: Config,
        scraper: WebScraper,
        site_identifier: SiteIdentifier,
    ) -> None:
        self.config = config
        self.scraper = scraper
        self.site_identifier = site_identifier
        self.finder = DocumentationFinder(config, site_identifier)
    
    async def load_from_file(
        self,
        file_content: str,
        file_name: str,
        file_type: Optional[str] = None,
    ) -> LoadedDocumentation:
        """Load documentation from uploaded file content.
        
        Supports: .md, .html, .txt, .rst
        """
        # Detect file type from extension if not provided
        if not file_type:
            ext = Path(file_name).suffix.lower()
            file_type = ext.lstrip(".")
        
        # Parse content based on file type
        if file_type in ("md", "markdown"):
            markdown = file_content
            text = file_content  # Markdown is readable as text
            html = ""
        elif file_type in ("html", "htm"):
            from bs4 import BeautifulSoup
            from markdownify import markdownify
            
            soup = BeautifulSoup(file_content, "lxml")
            text = soup.get_text("\n")
            markdown = markdownify(file_content, heading_style="ATX")
            html = file_content
        elif file_type in ("txt", "text"):
            text = file_content
            markdown = file_content
            html = ""
        elif file_type in ("rst", "restructuredtext"):
            # Basic RST handling - treat as text
            text = file_content
            markdown = file_content
            html = ""
        else:
            # Default: treat as plain text
            text = file_content
            markdown = file_content
            html = ""
        
        # Create a ScrapedPage from the file
        page = ScrapedPage(
            url=f"file://{file_name}",
            title=Path(file_name).stem,
            html=html,
            text=text,
            markdown=markdown,
            links=[],
            metadata={
                "source_type": "file_upload",
                "file_name": file_name,
                "file_type": file_type,
            },
        )
        
        LOGGER.info("Loaded documentation from file: %s", file_name)
        
        return LoadedDocumentation(
            method=LoadMethod.FILE_UPLOAD,
            pages=[page],
            source=file_name,
            metadata={
                "file_type": file_type,
                "content_length": len(file_content),
            },
        )
    
    async def load_from_url(
        self,
        url: str,
        follow_links: bool = False,
        max_pages: int = 10,
        link_depth: int = 1,
    ) -> LoadedDocumentation:
        """Load documentation from a URL.
        
        Optionally follows links to scrape multiple pages.
        """
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        pages: List[ScrapedPage] = []
        scraped_urls = set()
        
        # Scrape the main page
        main_page = await self.scraper.scrape(url)
        if not main_page:
            raise ValueError(f"Failed to scrape URL: {url}")
        
        pages.append(main_page)
        scraped_urls.add(url)
        
        # Optionally follow links
        if follow_links and link_depth > 0:
            base_domain = parsed.netloc
            
            # Get links from main page
            links_to_follow = []
            for link in main_page.links:
                link_parsed = urlparse(link)
                # Only follow links on the same domain
                if link_parsed.netloc == base_domain and link not in scraped_urls:
                    links_to_follow.append(link)
            
            # Limit number of links to follow
            links_to_follow = links_to_follow[:max_pages - 1]
            
            # Scrape linked pages
            if links_to_follow:
                linked_pages = await self.scraper.scrape_many(links_to_follow)
                for page in linked_pages:
                    if page.url not in scraped_urls:
                        pages.append(page)
                        scraped_urls.add(page.url)
                        
                        if len(pages) >= max_pages:
                            break
        
        LOGGER.info("Loaded %d pages from URL: %s", len(pages), url)
        
        return LoadedDocumentation(
            method=LoadMethod.URL,
            pages=pages,
            source=url,
            metadata={
                "base_url": url,
                "followed_links": follow_links,
                "pages_scraped": len(pages),
            },
        )
    
    async def load_by_name(
        self,
        name: str,
        auto_scrape: bool = True,
        max_pages: int = 5,
        follow_links: bool = True,
    ) -> LoadedDocumentation:
        """Find and load documentation by library/framework name.
        
        Uses AI-powered search to find the best documentation sites.
        """
        # Find documentation sites
        candidates = await self.finder.find_documentation(name, max_results=max_pages)
        
        if not candidates:
            raise ValueError(f"Could not find documentation for: {name}")
        
        pages: List[ScrapedPage] = []
        scraped_urls = set()
        
        if auto_scrape:
            # Scrape the top candidates
            for candidate in candidates:
                if len(pages) >= max_pages:
                    break
                
                if candidate.url in scraped_urls:
                    continue
                
                try:
                    result = await self.load_from_url(
                        candidate.url,
                        follow_links=follow_links,
                        max_pages=max(1, max_pages - len(pages)),
                        link_depth=1 if follow_links else 0,
                    )
                    
                    for page in result.pages:
                        if page.url not in scraped_urls:
                            pages.append(page)
                            scraped_urls.add(page.url)
                            
                            if len(pages) >= max_pages:
                                break
                                
                except Exception as exc:
                    LOGGER.warning("Failed to scrape %s: %s", candidate.url, exc)
        
        LOGGER.info(
            "Found and loaded %d pages for '%s' from %d candidates",
            len(pages),
            name,
            len(candidates),
        )
        
        return LoadedDocumentation(
            method=LoadMethod.NAME_SEARCH,
            pages=pages,
            source=name,
            metadata={
                "search_name": name,
                "candidates_found": len(candidates),
                "candidate_urls": [c.url for c in candidates],
                "pages_scraped": len(pages),
            },
        )
    
    async def load(
        self,
        source: str,
        source_type: Optional[str] = None,
        **kwargs,
    ) -> LoadedDocumentation:
        """Unified load method that auto-detects source type.
        
        Args:
            source: File content, URL, or documentation name
            source_type: Optional hint - "file", "url", or "name"
            **kwargs: Additional arguments passed to specific loaders
        
        Returns:
            LoadedDocumentation with scraped pages
        """
        # Auto-detect source type if not provided
        if source_type is None:
            source_type = self._detect_source_type(source)
        
        if source_type == "url":
            return await self.load_from_url(source, **kwargs)
        elif source_type == "file":
            file_name = kwargs.pop("file_name", "uploaded_doc.md")
            return await self.load_from_file(source, file_name, **kwargs)
        elif source_type == "name":
            return await self.load_by_name(source, **kwargs)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    def _detect_source_type(self, source: str) -> str:
        """Detect the type of source from its content."""
        # Check if it's a URL
        if source.startswith(("http://", "https://", "www.")):
            return "url"
        
        # Check if it looks like file content (multi-line with markdown/html)
        if "\n" in source and len(source) > 200:
            return "file"
        
        # Check if it's a file path
        if "/" in source or "\\" in source:
            path = Path(source)
            if path.suffix in (".md", ".html", ".txt", ".rst"):
                return "file"
        
        # Default to name search
        return "name"
