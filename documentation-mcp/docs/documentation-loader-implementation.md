# Documentation Loader Implementation

## Project Summary

This implementation adds flexible documentation loading capabilities to the Documentation MCP server. Users can now load documentation in three ways:
1. **Upload a file** - Markdown, HTML, TXT, or RST files
2. **Provide a URL** - Direct link to documentation
3. **Search by name** - AI-powered agent finds and scrapes documentation automatically

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DocumentationMCPServer                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  DocumentationLoader                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │   │
│  │  │ load_from_ │  │ load_from_ │  │   load_by_name     │  │   │
│  │  │   file()   │  │   url()    │  │  (AI-powered)      │  │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────────┬──────────┘  │   │
│  │        │               │                    │             │   │
│  │        └───────────────┼────────────────────┘             │   │
│  │                        │                                  │   │
│  │                        ▼                                  │   │
│  │              ┌─────────────────────┐                      │   │
│  │              │ DocumentationFinder │                      │   │
│  │              │   (AI Search Agent) │                      │   │
│  │              └─────────────────────┘                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Terminology Extraction & Indexing            │   │
│  │  • Extract terms from loaded pages                        │   │
│  │  • Index in Zoekt for fast search                         │   │
│  │  • Build knowledge graph relationships                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
src/
├── documentation_loader.py    # NEW: Main loader with 3 input methods
├── server.py                  # MODIFIED: Added documentation loading tools
└── ...
```

## New MCP Tools

### 1. `load_documentation_from_url`

Load documentation directly from a URL.

```python
# Example usage
result = await load_documentation_from_url(
    url="https://fastapi.tiangolo.com/",
    follow_links=True,   # Scrape linked pages too
    max_pages=10         # Limit total pages
)
```

**Response:**
```json
{
    "method": "URL",
    "source": "https://fastapi.tiangolo.com/",
    "page_count": 5,
    "total_content_length": 45000,
    "pages": [
        {"url": "...", "title": "FastAPI", "content_length": 12000}
    ],
    "terminology": {
        "terms_extracted": 42,
        "pages_indexed": 5
    }
}
```

### 2. `load_documentation_from_file`

Load documentation from uploaded file content.

```python
# Example usage
result = await load_documentation_from_file(
    file_content="# My API\n\n## Authentication\n...",
    file_name="api-docs.md",
    file_type="md"  # Optional, auto-detected from extension
)
```

**Supported file types:**
- `.md` / `.markdown` - Markdown files
- `.html` / `.htm` - HTML files
- `.txt` / `.text` - Plain text files
- `.rst` - reStructuredText files

### 3. `load_documentation_by_name`

AI-powered search to find and load documentation by name.

```python
# Example usage
result = await load_documentation_by_name(
    name="React",           # Library/framework name
    auto_scrape=True,       # Automatically scrape found docs
    max_pages=5,            # Limit pages to scrape
    follow_links=True       # Follow links on doc pages
)
```

**How it works:**
1. AI generates optimal search queries for the name
2. DuckDuckGo search finds candidate documentation sites
3. AI ranks candidates by relevance (prefers official docs)
4. Top candidates are scraped and indexed

### 4. `find_documentation`

Find documentation sites without scraping (preview mode).

```python
# Example usage
result = await find_documentation(
    name="pandas",
    max_results=5
)
```

**Response:**
```json
{
    "name": "pandas",
    "candidates": [
        {
            "title": "pandas documentation",
            "url": "https://pandas.pydata.org/docs/",
            "snippet": "pandas is a fast, powerful...",
            "confidence": 0.95
        }
    ],
    "count": 5
}
```

### 5. `terminology_search`

Search using terminology-aware search after loading docs.

```python
result = await terminology_search(
    query="How do I handle authentication?",
    use_knowledge_graph=True
)
```

### 6. `get_term_info`

Get detailed information about a specific term.

```python
result = await get_term_info(term="useState")
```

### 7. `get_terminology_stats`

Get statistics about indexed terminology.

```python
result = await get_terminology_stats()
```

## Key Components

### DocumentationLoader (`src/documentation_loader.py`)

Main class that handles all three loading methods.

```python
class DocumentationLoader:
    async def load_from_file(file_content, file_name, file_type) -> LoadedDocumentation
    async def load_from_url(url, follow_links, max_pages) -> LoadedDocumentation
    async def load_by_name(name, auto_scrape, max_pages) -> LoadedDocumentation
    async def load(source, source_type, **kwargs) -> LoadedDocumentation  # Auto-detect
```

### DocumentationFinder (`src/documentation_loader.py`)

AI-powered agent that finds documentation by name.

```python
class DocumentationFinder:
    async def find_documentation(name, max_results) -> List[SiteCandidate]
    async def _generate_search_queries(name) -> List[str]  # AI-generated
    async def _rank_candidates(name, candidates) -> List[SiteCandidate]  # AI-ranked
```

### LoadedDocumentation

Result dataclass returned by all loading methods.

```python
@dataclass
class LoadedDocumentation:
    method: LoadMethod      # FILE_UPLOAD, URL, or NAME_SEARCH
    pages: List[ScrapedPage]
    source: str             # Original input
    metadata: Dict[str, Any]
```

## Usage Examples

### Example 1: Load React Documentation by Name

```python
# User says: "Load React documentation"

result = await load_documentation_by_name("React")

# System:
# 1. AI generates queries: ["react official documentation", "reactjs.org", ...]
# 2. Searches DuckDuckGo for each query
# 3. AI ranks results, picks https://react.dev/
# 4. Scrapes React documentation pages
# 5. Extracts terminology: useState, useEffect, JSX, components, ...
# 6. Builds knowledge graph relationships
# 7. Returns result with 5 pages, 67 terms extracted
```

### Example 2: Load from URL

```python
# User provides a direct link

result = await load_documentation_from_url(
    url="https://docs.python.org/3/library/asyncio.html",
    follow_links=True,
    max_pages=10
)

# System scrapes the page and linked pages
# Extracts: asyncio, coroutine, await, Task, Future, ...
```

### Example 3: Upload Documentation File

```python
# User uploads their internal API documentation

result = await load_documentation_from_file(
    file_content="""
    # Internal API Documentation
    
    ## Authentication
    
    Use `Bearer` tokens for authentication.
    
    ```python
    headers = {"Authorization": f"Bearer {token}"}
    ```
    
    ## Endpoints
    
    ### GET /users
    Returns a list of users.
    """,
    file_name="internal-api.md"
)

# System extracts: Authentication, Bearer, token, Endpoints, users, ...
```

### Example 4: Search After Loading

```python
# After loading documentation, search with terminology awareness

result = await terminology_search("How do I use hooks?")

# Returns:
# - Answer with terminology context
# - Selected terms: React Hooks, useState, useEffect
# - Related concepts from knowledge graph
```

## Integration Flow

```
┌─────────────────┐
│  User Request   │
│  (file/URL/name)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DocumentLoader  │
│ (detect method) │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌───────┐ ┌────────────┐
│ File  │ │  URL  │ │ Name Search│
│ Parse │ │ Scrape│ │ (AI Agent) │
└───┬───┘ └───┬───┘ └─────┬──────┘
    │         │           │
    └────┬────┴───────────┘
         │
         ▼
┌─────────────────┐
│ ScrapedPage(s)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Terminology     │
│ Extraction      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Zoekt Indexing  │
│ + Knowledge     │
│   Graph         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Ready for       │
│ Queries!        │
└─────────────────┘
```

## Configuration

No additional configuration required. Uses existing settings:

```yaml
# config/config.yaml

ai:
  model: "gpt-3.5-turbo"  # Used for AI search agent

scraping:
  max_concurrent_requests: 5
  request_delay: 1.0
  timeout: 30

terminology:
  enabled: true
  auto_extract_on_scrape: true
```

## Error Handling

- **Invalid URL**: Returns error with message
- **Failed scrape**: Logs warning, continues with other pages
- **No documentation found**: Returns error with search suggestions
- **AI unavailable**: Falls back to heuristic search/ranking

## API Reference

### DocumentationLoader Methods

| Method | Description |
|--------|-------------|
| `load_from_file(content, name, type)` | Load from file content |
| `load_from_url(url, follow_links, max_pages)` | Load from URL |
| `load_by_name(name, auto_scrape, max_pages)` | AI-powered search and load |
| `load(source, source_type, **kwargs)` | Auto-detect and load |

### DocumentationFinder Methods

| Method | Description |
|--------|-------------|
| `find_documentation(name, max_results)` | Find doc sites by name |

### MCP Tools

| Tool | Description |
|------|-------------|
| `load_documentation_from_url` | Load docs from URL |
| `load_documentation_from_file` | Load docs from file |
| `load_documentation_by_name` | AI search and load |
| `find_documentation` | Find docs without scraping |
| `terminology_search` | Search with terminology |
| `get_term_info` | Get term details |
| `get_terminology_stats` | Get system stats |
