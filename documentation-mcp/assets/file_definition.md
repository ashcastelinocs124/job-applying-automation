# Documentation MCP Implementation

## Project Summary
The Documentation MCP server enables coding agents to retrieve up-to-date documentation context in real time. It identifies relevant documentation sites, scrapes and normalizes their content, chunks and embeds the text for semantic retrieval, and performs agentic RAG to produce grounded answers. The server exposes these capabilities through MCP tools that any compatible agent can call.

## Architecture Overview
```
documentation-mcp/
├── config/
│   └── config.yaml              # Runtime configuration
├── src/
│   ├── __init__.py              # Package export list
│   ├── agentic_rag.py           # RAG coordination engine
│   ├── cache_manager.py         # TTL cache for scraped data
│   ├── content_processor.py     # Chunking and embedding utilities
│   ├── context_builder.py       # Response formatting helpers
│   ├── deep_search.py           # Recursive exploration orchestrator
│   ├── server.py                # MCP server wiring and tool registration
│   ├── settings.py              # Typed configuration loader
│   ├── site_identifier.py       # Documentation site discovery
│   └── web_scraper.py           # Async scraping and normalization
├── documentation-mcp-server.py  # CLI entry point
├── requirements.txt             # Python dependencies
└── documentation-mcp-implementation.md
```

## File Structure
- `requirements.txt` – dependency list (MCP SDK, aiohttp, BeautifulSoup, embeddings, etc.)
- `config/config.yaml` – server, scraping, cache, RAG, AI, and site-pattern settings
- `src/settings.py` – loads YAML into dataclasses with env overrides
- `src/cache_manager.py` – thread-safe TTL cache for pages/chunks
- `src/site_identifier.py` – searches DuckDuckGo to find documentation URLs
- `src/web_scraper.py` – throttled async scraper producing HTML/text/markdown + links
- `src/content_processor.py` – splits documents into overlapping chunks and embeds them
- `src/deep_search.py` – explores related topics by following documentation links
- `src/agentic_rag.py` – orchestrates site discovery, chunk ranking, answer composition
- `src/context_builder.py` – helper utilities for MCP responses (extensible)
- `src/server.py` – FastMCP server registering tools: search_documentation, get_site_context, explore_related, get_examples, validate_info
- `documentation-mcp-server.py` – CLI launcher wrapping the async server
- `documentation-mcp-implementation.md` – this documentation

## Key Components
1. **Settings Loader (`settings.py`)** – Provides strongly typed access to configuration with helpful errors.
2. **Caching Layer (`cache_manager.py`)** – Avoids redundant scraping by hashing request parameters and expiring entries by TTL.
3. **Site Identifier (`site_identifier.py`)** – Uses DuckDuckGo search plus hostname heuristics to prioritize official docs.
4. **Web Scraper (`web_scraper.py`)** – Applies request throttling, readability extraction, markdown conversion, and link harvesting.
5. **Content Processor (`content_processor.py`)** – Generates overlapping word chunks and embeds them via SentenceTransformers.
6. **Agentic RAG Engine (`agentic_rag.py`)** – Coordinates site selection, embedding similarity scoring, LLM-based answer synthesis, code example extraction, and statement validation. Falls back to templated responses if no LLM API key is available.
7. **Deep Search (`deep_search.py`)** – Recursively follows top documentation links to build a knowledge graph for broader exploration.
8. **MCP Server (`server.py`)** – Wires components into FastMCP tools so other agents can invoke capabilities programmatically.

## Installation & Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment**
   - Copy `config/config.yaml` and adjust settings as needed.
   - Optionally set `DOCUMENTATION_MCP_CONFIG` to point to a custom config file.
   - Provide `OPENAI_API_KEY` if LLM-backed answers are desired.
3. **Run the server**
   ```bash
   python src/documentation-mcp-server.py --config config/config.yaml
   ```
4. **Register with MCP clients**
   - Add the executable path to your MCP configuration (e.g., Cursor, Windsurf).

## Usage Examples
- **Search documentation**
  ```json
  {
    "tool": "search_documentation",
    "params": {"query": "How to configure FastAPI routers", "code_context": "app = FastAPI()"}
  }
  ```
- **Get site-specific context**
  ```json
  {
    "tool": "get_site_context",
    "params": {"site_url": "https://fastapi.tiangolo.com/tutorial/routers/"}
  }
  ```
- **Explore related topics**
  ```json
  {
    "tool": "explore_related",
    "params": {"topic": "LangChain memory", "depth": 2}
  }
  ```
- **Retrieve examples**
  ```json
  {
    "tool": "get_examples",
    "params": {"query": "pandas merge examples", "language": "python"}
  }
  ```
- **Validate statements**
  ```json
  {
    "tool": "validate_info",
    "params": {"statement": "Next.js supports app router server actions"}
  }
  ```

## Configuration
Key knobs in `config/config.yaml`:
- `server`: host/port/name/version metadata.
- `scraping`: concurrency, delay, timeout, user-agent tuning.
- `cache`: TTL, capacity, storage path stub (in-memory in current version).
- `rag`: embedding model, chunk sizing, and context limits.
- `ai`: LLM model, temperature, and token cap (used if API key is present).
- `sites`: hostname patterns and exclusions for prioritizing official docs.
Override via environment variable `DOCUMENTATION_MCP_CONFIG` or by editing the YAML directly.

## Troubleshooting
- **No results returned**: ensure outbound network access for DuckDuckGo and target docs; check patterns/exclusions.
- **Slow scraping**: adjust `scraping.max_concurrent_requests` and `request_delay`, but respect target site rate limits.
- **Missing embeddings**: verify SentenceTransformers model download (may require internet on first run).
- **LLM errors**: confirm `OPENAI_API_KEY` and chosen `ai.model` are available; fallback summaries will still work without an API key.
- **High memory usage**: lower `rag.chunk_size` or reduce `cache.max_size`.

## Usage Notes
- The system is designed for stateless MCP calls; persistent caches live in memory. Persisted storage can be added via `cache.storage_path` in future iterations.
- Deep search depth is capped to prevent runaway crawls; adjust `depth` parameter per query as needed.

This document ensures you can understand, operate, and extend the Documentation MCP server implemented in this project.
