"""Main MCP server implementation for documentation retrieval."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .agentic_rag import AgenticRAGEngine
from .cache_manager import CacheManager
from .content_processor import ContentProcessor
from .deep_search import DeepSearchOrchestrator
from .documentation_loader import DocumentationLoader, LoadedDocumentation
from .enhanced_search import EnhancedSearchEngine
from .proactive.indexer import ProactiveIndexer
from .settings import Config, load_config
from .site_identifier import SiteIdentifier
from .web_scraper import WebScraper

LOGGER = logging.getLogger(__name__)


class DocumentationMCPServer:
    """Coordinates components and exposes MCP tools."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.app = FastMCP(
            server_name=config.server.name, server_version=config.server.version
        )

        # Core components
        self.cache = CacheManager(config)
        self.site_identifier = SiteIdentifier(config)
        self.web_scraper = WebScraper(config)
        self.content_processor = ContentProcessor(config)

        # Deep search
        self.deep_search = DeepSearchOrchestrator(
            config,
            identifier=self.site_identifier,
            scraper=self.web_scraper,
        )

        # RAG engine
        self.rag_engine = AgenticRAGEngine(
            config,
            identifier=self.site_identifier,
            scraper=self.web_scraper,
            processor=self.content_processor,
            cache=self.cache,
            deep_search=self.deep_search,
        )

        # Proactive indexer (Zoekt + Point Lists)
        self.proactive_indexer = ProactiveIndexer(
            config,
            identifier=self.site_identifier,
            scraper=self.web_scraper,
        )

        # Enhanced search (unified Zoekt + Point List search)
        self.enhanced_search = EnhancedSearchEngine(
            config,
            proactive_indexer=self.proactive_indexer,
        )

        # Documentation loader (file, URL, or name search)
        self.doc_loader = DocumentationLoader(
            config,
            scraper=self.web_scraper,
            site_identifier=self.site_identifier,
        )

        self._register_tools()

    def _register_tools(self) -> None:
        # ============= Existing Tools =============

        @self.app.tool()
        async def search_documentation(
            query: str, code_context: Optional[str] = None
        ) -> dict:
            """Primary tool to search documentation for the given query."""
            LOGGER.info("search_documentation invoked", extra={"query": query})
            return await self.rag_engine.search(query=query, code_context=code_context)

        @self.app.tool()
        async def get_site_context(site_url: str, topic: Optional[str] = None) -> dict:
            """Fetches deeper context for a specific documentation site."""
            LOGGER.info("get_site_context invoked", extra={"site_url": site_url})
            return await self.rag_engine.get_site_context(
                site_url=site_url, topic=topic
            )

        @self.app.tool()
        async def explore_related(topic: str, depth: int = 1) -> dict:
            """Recursively explores related documentation topics."""
            LOGGER.info(
                "explore_related invoked", extra={"topic": topic, "depth": depth}
            )
            return await self.deep_search.explore(topic=topic, depth=depth)

        @self.app.tool()
        async def get_examples(query: str, language: Optional[str] = None) -> dict:
            """Retrieves code examples relevant to the query."""
            LOGGER.info(
                "get_examples invoked", extra={"query": query, "language": language}
            )
            return await self.rag_engine.get_examples(query=query, language=language)

        @self.app.tool()
        async def validate_info(statement: str) -> dict:
            """Validates documentation statements across multiple sources."""
            LOGGER.info("validate_info invoked")
            return await self.rag_engine.validate_statement(statement)

        # ============= New Enhanced Search Tools =============

        @self.app.tool()
        async def instant_search(
            query: str,
            include_code: bool = True,
            include_concepts: bool = True,
            language: Optional[str] = None,
            max_results: int = 10,
        ) -> Dict[str, Any]:
            """Instant search combining Zoekt code search with point list knowledge.

            Provides sub-100ms responses for indexed documentation.
            Returns code snippets, concepts, functions, and a natural language summary.
            """
            LOGGER.info("instant_search invoked", extra={"query": query})
            result = await self.enhanced_search.search(
                query,
                include_code=include_code,
                include_points=include_concepts,
                include_related=True,
                generate_response=True,
                max_results=max_results,
                language=language,
            )
            return result.to_dict()

        @self.app.tool()
        async def search_code(
            query: str,
            language: Optional[str] = None,
            limit: int = 10,
        ) -> Dict[str, Any]:
            """Fast code search via Zoekt.

            Searches indexed documentation code blocks for matching patterns.
            Supports language filtering and regex patterns.
            """
            LOGGER.info(
                "search_code invoked", extra={"query": query, "language": language}
            )
            results = await self.enhanced_search.search_code(
                query, language=language, limit=limit
            )
            return {
                "query": query,
                "results": [
                    {
                        "file_path": r.file_path,
                        "language": r.language,
                        "snippet": r.snippet,
                        "line_number": r.line_number,
                        "context": r.context,
                        "score": r.score,
                        "source_url": r.source_url,
                    }
                    for r in results
                ],
                "count": len(results),
            }

        @self.app.tool()
        async def search_concepts(
            query: str,
            limit: int = 10,
        ) -> Dict[str, Any]:
            """Search for concepts, functions, and classes in documentation.

            Returns structured knowledge points extracted from indexed documentation.
            """
            LOGGER.info("search_concepts invoked", extra={"query": query})
            results = await self.enhanced_search.search_concepts(query, limit=limit)
            return {
                "query": query,
                "results": [
                    {
                        "id": p.id,
                        "type": p.point_type.name,
                        "name": p.name,
                        "description": p.description,
                        "source_url": p.source_url,
                        "confidence": p.confidence,
                        "metadata": p.metadata,
                    }
                    for p in results
                ],
                "count": len(results),
            }

        @self.app.tool()
        async def find_code_examples(
            topic: str,
            language: Optional[str] = None,
            limit: int = 5,
        ) -> Dict[str, Any]:
            """Find code examples for a specific topic.

            Returns real code examples from indexed documentation.
            """
            LOGGER.info("find_code_examples invoked", extra={"topic": topic})
            examples = await self.enhanced_search.find_examples(
                topic, language=language, limit=limit
            )
            return {
                "topic": topic,
                "examples": examples,
                "count": len(examples),
            }

        # ============= Proactive Indexing Tools =============

        @self.app.tool()
        async def index_topic(
            topic: str,
            limit: int = 5,
        ) -> Dict[str, Any]:
            """Proactively index documentation for a topic.

            Discovers and indexes relevant documentation sites in the background.
            Returns immediately with task IDs for tracking progress.
            """
            LOGGER.info("index_topic invoked", extra={"topic": topic})
            return await self.proactive_indexer.index_topic(topic, limit=limit)

        @self.app.tool()
        async def index_url(
            url: str,
            topic: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Index a specific documentation URL.

            Extracts code blocks for Zoekt and builds point lists.
            Returns a task ID for tracking progress.
            """
            LOGGER.info("index_url invoked", extra={"url": url})
            task_id = await self.proactive_indexer.schedule_indexing(url, topic=topic)
            return {
                "url": url,
                "task_id": task_id,
                "status": "scheduled" if task_id else "already_pending",
            }

        @self.app.tool()
        async def get_indexing_status(task_id: str) -> Dict[str, Any]:
            """Get the status of an indexing task."""
            LOGGER.info("get_indexing_status invoked", extra={"task_id": task_id})
            status = await self.proactive_indexer.get_task_status(task_id)
            if status is None:
                return {"error": "Task not found", "task_id": task_id}
            return status

        @self.app.tool()
        async def get_index_stats() -> Dict[str, Any]:
            """Get statistics about the current indexes.

            Returns information about indexed URLs, point lists, and Zoekt status.
            """
            LOGGER.info("get_index_stats invoked")
            return self.proactive_indexer.get_stats()

        # ============= Documentation Loading Tools =============

        @self.app.tool()
        async def load_documentation_from_url(
            url: str,
            follow_links: bool = False,
            max_pages: int = 10,
        ) -> Dict[str, Any]:
            """Load documentation from a URL.

            Scrapes the documentation page and optionally follows links to get
            related pages. Automatically extracts terminology and builds knowledge graph.

            Args:
                url: The documentation URL to load
                follow_links: Whether to follow links on the page
                max_pages: Maximum number of pages to scrape

            Returns:
                Information about loaded documentation including page count and extracted terms
            """
            LOGGER.info("load_documentation_from_url invoked", extra={"url": url})
            
            result = await self.doc_loader.load_from_url(
                url,
                follow_links=follow_links,
                max_pages=max_pages,
            )
            
            # Extract terminology and index
            terminology_results = await self._process_loaded_documentation(result)
            
            return {
                **result.to_dict(),
                "terminology": terminology_results,
            }

        @self.app.tool()
        async def load_documentation_from_file(
            file_content: str,
            file_name: str,
            file_type: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Load documentation from uploaded file content.

            Supports markdown (.md), HTML (.html), plain text (.txt), and RST (.rst) files.
            Automatically extracts terminology and builds knowledge graph.

            Args:
                file_content: The content of the documentation file
                file_name: Name of the file (used for type detection)
                file_type: Optional file type hint (md, html, txt, rst)

            Returns:
                Information about loaded documentation including extracted terms
            """
            LOGGER.info("load_documentation_from_file invoked", extra={"file_name": file_name})
            
            result = await self.doc_loader.load_from_file(
                file_content,
                file_name,
                file_type=file_type,
            )
            
            # Extract terminology and index
            terminology_results = await self._process_loaded_documentation(result)
            
            return {
                **result.to_dict(),
                "terminology": terminology_results,
            }

        @self.app.tool()
        async def load_documentation_by_name(
            name: str,
            auto_scrape: bool = True,
            max_pages: int = 5,
            follow_links: bool = True,
        ) -> Dict[str, Any]:
            """Find and load documentation by library/framework name.

            Uses AI-powered search to find the official documentation for a library,
            framework, or tool. Automatically scrapes and indexes the documentation.

            Examples:
                - "React" -> finds and loads React documentation
                - "FastAPI" -> finds and loads FastAPI docs
                - "pandas" -> finds and loads pandas documentation

            Args:
                name: Name of the library, framework, or tool
                auto_scrape: Whether to automatically scrape found documentation
                max_pages: Maximum number of pages to scrape
                follow_links: Whether to follow links on documentation pages

            Returns:
                Information about found and loaded documentation
            """
            LOGGER.info("load_documentation_by_name invoked", extra={"name": name})
            
            result = await self.doc_loader.load_by_name(
                name,
                auto_scrape=auto_scrape,
                max_pages=max_pages,
                follow_links=follow_links,
            )
            
            # Extract terminology and index
            terminology_results = await self._process_loaded_documentation(result)
            
            return {
                **result.to_dict(),
                "terminology": terminology_results,
            }

        @self.app.tool()
        async def find_documentation(
            name: str,
            max_results: int = 5,
        ) -> Dict[str, Any]:
            """Find documentation sites for a library/framework without scraping.

            Returns a list of candidate documentation URLs that can be loaded
            using load_documentation_from_url.

            Args:
                name: Name of the library, framework, or tool
                max_results: Maximum number of candidates to return

            Returns:
                List of documentation site candidates with URLs and descriptions
            """
            LOGGER.info("find_documentation invoked", extra={"name": name})
            
            candidates = await self.doc_loader.finder.find_documentation(
                name,
                max_results=max_results,
            )
            
            return {
                "name": name,
                "candidates": [
                    {
                        "title": c.title,
                        "url": c.url,
                        "snippet": c.snippet,
                        "confidence": c.confidence,
                    }
                    for c in candidates
                ],
                "count": len(candidates),
            }

        @self.app.tool()
        async def terminology_search(
            query: str,
            use_knowledge_graph: bool = True,
        ) -> Dict[str, Any]:
            """Search using terminology-aware search.

            Enhanced search that leverages extracted terminology and knowledge graph
            for better results. Use this after loading documentation.

            Args:
                query: The search query
                use_knowledge_graph: Whether to include knowledge graph results

            Returns:
                Search results with terminology context and related concepts
            """
            LOGGER.info("terminology_search invoked", extra={"query": query})
            return await self.rag_engine.terminology_aware_search(
                query,
                use_knowledge_graph=use_knowledge_graph,
            )

        @self.app.tool()
        async def get_term_info(term: str) -> Dict[str, Any]:
            """Get detailed information about a term from the knowledge graph.

            Returns hierarchical relationships, related terms, and definitions.

            Args:
                term: The term to look up

            Returns:
                Term hierarchy and relationships
            """
            LOGGER.info("get_term_info invoked", extra={"term": term})
            return await self.rag_engine.get_term_hierarchy(term)

        @self.app.tool()
        async def get_terminology_stats() -> Dict[str, Any]:
            """Get statistics about the terminology system.

            Returns information about indexed terms and knowledge graph.
            """
            LOGGER.info("get_terminology_stats invoked")
            return await self.rag_engine.get_terminology_stats()

    async def _process_loaded_documentation(
        self,
        loaded: LoadedDocumentation,
    ) -> Dict[str, Any]:
        """Process loaded documentation: extract terminology and index."""
        total_terms = 0
        indexed_pages = 0
        
        for page in loaded.pages:
            try:
                # Extract and index terminology
                result = await self.rag_engine.extract_and_index_terminology(page)
                if result.get("status") == "success":
                    total_terms += result.get("terms_extracted", 0)
                    indexed_pages += 1
                
                # Also index for code search
                await self.proactive_indexer.schedule_indexing(
                    page.url,
                    topic=loaded.source,
                )
                
            except Exception as exc:
                LOGGER.warning("Failed to process page %s: %s", page.url, exc)
        
        return {
            "terms_extracted": total_terms,
            "pages_indexed": indexed_pages,
        }

    async def _start_background_services(self) -> None:
        """Start background services like proactive indexing."""
        if self.config.proactive.enabled:
            await self.proactive_indexer.start()

    async def _stop_background_services(self) -> None:
        """Stop background services."""
        if self.config.proactive.enabled:
            await self.proactive_indexer.stop()
        await self.enhanced_search.close()

    async def run(self) -> None:
        """Starts the MCP server blocking run loop."""
        LOGGER.info(
            "Starting Documentation MCP server",
            extra={"host": self.config.server.host, "port": self.config.server.port},
        )

        # Start background services
        await self._start_background_services()

        try:
            await self.app.run(
                host=self.config.server.host, port=self.config.server.port
            )
        finally:
            await self._stop_background_services()


async def main(config_path: Optional[str] = None) -> None:
    """Entrypoint for launching the server."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    config = load_config(config_path)
    server = DocumentationMCPServer(config)
    await server.run()


def run_sync(config_path: Optional[str] = None) -> None:
    """Synchronous adapter for launching the server."""
    asyncio.run(main(config_path))


if __name__ == "__main__":
    run_sync()
