# Terminology System Implementation

## Project Summary

This implementation adds an AI-powered terminology extraction and knowledge graph system to the Documentation MCP server. The system automatically identifies important terms from documentation, indexes them using Zoekt for fast search, and builds a knowledge graph of relationships between terms.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AgenticRAGEngine                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │TerminologyExtractor│ │TerminologyIndexer│ │  TermSelector │  │
│  │  (AI + Heuristic)  │ │   (Zoekt-based)  │ │  (AI Agent)   │  │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬───────┘  │
│           │                    │                     │          │
│           └────────────────────┼─────────────────────┘          │
│                                │                                 │
│                    ┌───────────▼───────────┐                    │
│                    │    KnowledgeGraph     │                    │
│                    │  (Enhanced with Terms)│                    │
│                    └───────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Documentation Loaded** → `TerminologyExtractor` identifies important terms
2. **Terms Extracted** → `TerminologyIndexer` stores terms in Zoekt-compatible format
3. **User Query** → `TerminologyIndexer.search_terms()` performs Zoekt search
4. **Search Results** → `TermSelector` (AI agent) picks the best matching terms
5. **Selected Terms** → `KnowledgeGraph` provides related concepts and hierarchy
6. **Combined Results** → Enhanced answer with terminology context

## File Structure

```
src/
├── terminology/
│   ├── __init__.py          # Package exports
│   ├── extractor.py         # AI-powered term extraction
│   ├── indexer.py           # Zoekt-based term indexing
│   └── selector.py          # AI agent for term selection
├── point_list/
│   └── knowledge.py         # Enhanced with terminology support
├── agentic_rag.py           # Integrated terminology-aware search
└── settings.py              # Added TerminologySettings
config/
└── config.yaml              # Added terminology configuration
```

## Key Components

### 1. TerminologyExtractor (`src/terminology/extractor.py`)

Extracts important terminology from documentation using both AI and heuristics.

**Term Types:**
- `TECHNICAL_TERM` - General technical terms
- `FUNCTION_NAME` - Function/method names from code
- `CLASS_NAME` - Class definitions
- `METHOD_NAME` - Method names
- `VARIABLE_NAME` - Variable names
- `CONCEPT` - Conceptual terms from headings
- `ACRONYM` - Acronyms with definitions
- `DOMAIN_SPECIFIC` - Domain-specific terminology

**Extraction Methods:**
- **Heuristic extraction**: Pattern matching for PascalCase, camelCase, snake_case, acronyms
- **Code entity extraction**: Parses code blocks for function/class definitions
- **Concept extraction**: Extracts from headings and emphasized text
- **Acronym extraction**: Finds acronym definitions like "API (Application Programming Interface)"
- **AI extraction**: Uses OpenAI to identify domain-specific terms

**Usage:**
```python
extractor = TerminologyExtractor(config)
terms = await extractor.extract_from_page(scraped_page)
```

### 2. TerminologyIndexer (`src/terminology/indexer.py`)

Indexes extracted terms using Zoekt for fast full-text search.

**Features:**
- Creates markdown files for each term with metadata
- Organizes terms by source URL
- Triggers Zoekt indexing when available
- Provides fallback local search when Zoekt is unavailable

**Usage:**
```python
indexer = TerminologyIndexer(config)
index_result = await indexer.index_terms(terms, "collection_name")
search_results = await indexer.search_terms("query", limit=10)
```

### 3. TermSelector (`src/terminology/selector.py`)

AI agent that intelligently selects the most relevant terms for a query.

**Selection Criteria:**
- Query relevance scoring
- Confidence threshold filtering
- Diversity enforcement (prevents too many terms of same type)
- Frequency boosting

**Features:**
- AI-powered relevance scoring using OpenAI
- Heuristic fallback when AI unavailable
- Generates human-readable selection reasons
- Finds similar terms for expansion

**Usage:**
```python
selector = TermSelector(config)
selected = await selector.select_terms(terms, query, criteria)
```

### 4. Enhanced KnowledgeGraph (`src/point_list/knowledge.py`)

Extended with terminology-specific relationships and search.

**New Relationship Types:**
- `SYNONYM_OF` - Synonymous terms
- `ANTONYM_OF` - Opposite terms
- `TERM_DEFINITION` - Definition relationships
- `TERM_USAGE` - Usage examples
- `TERM_CATEGORY` - Hierarchical categories
- `TERM_RELATED` - Semantic relationships

**New Methods:**
- `add_terminology(terms)` - Add terms to the graph
- `search_terminology(query)` - Search specifically in terminology nodes
- `get_term_hierarchy(term)` - Get hierarchical relationships

**Usage:**
```python
graph = KnowledgeGraph(config)
graph.add_terminology(terms)
results = graph.search_terminology("query", expand_related=True)
hierarchy = graph.get_term_hierarchy("term_name")
```

### 5. Integrated AgenticRAGEngine (`src/agentic_rag.py`)

New terminology-aware search methods.

**New Methods:**
- `extract_and_index_terminology(page)` - Extract and index terms from a page
- `terminology_aware_search(query)` - Enhanced search with terminology context
- `get_term_hierarchy(term)` - Get term relationships
- `get_terminology_stats()` - Get system statistics

**Usage:**
```python
# Extract terminology when loading documentation
result = await engine.extract_and_index_terminology(page)

# Perform terminology-aware search
result = await engine.terminology_aware_search(
    query="How do I use async functions?",
    use_knowledge_graph=True
)
```

## Configuration

Add to `config/config.yaml`:

```yaml
terminology:
  enabled: true                    # Enable/disable terminology system
  max_terms_per_page: 30           # Maximum terms to extract per page
  index_dir: "./terminology-index" # Directory for term index files
  use_ai_extraction: true          # Use AI for term extraction
  use_ai_selection: true           # Use AI for term selection
  confidence_threshold: 0.6        # Minimum confidence for terms
  build_knowledge_graph: true      # Build relationships between terms
  auto_extract_on_scrape: true     # Auto-extract when scraping pages
```

## Installation & Setup

1. **Dependencies** (already in requirements.txt):
   - `openai>=1.3.0` - For AI-powered extraction and selection
   - `aiohttp>=3.9.0` - For async HTTP requests to Zoekt

2. **Environment Variables**:
   ```bash
   export OPENAI_API_KEY="your-api-key"  # Required for AI features
   ```

3. **Zoekt Server** (optional but recommended):
   ```bash
   # Install Zoekt
   go install github.com/sourcegraph/zoekt/cmd/zoekt-webserver@latest
   
   # Start Zoekt server
   zoekt-webserver -listen :6070 -index ./terminology-index
   ```

## Usage Examples

### Basic Terminology Extraction

```python
from src.terminology import TerminologyExtractor
from src.settings import load_config

config = load_config()
extractor = TerminologyExtractor(config)

# Extract terms from a scraped page
terms = await extractor.extract_from_page(page)

for term in terms:
    print(f"{term.term} ({term.term_type.name}): {term.definition}")
```

### Terminology-Aware Search

```python
from src.agentic_rag import AgenticRAGEngine

# Initialize engine (with all dependencies)
engine = AgenticRAGEngine(config, ...)

# Perform enhanced search
result = await engine.terminology_aware_search(
    query="How do I implement authentication?",
    code_context="def login(user, password):",
    use_knowledge_graph=True
)

print(f"Answer: {result['answer']}")
print(f"Selected Terms: {result['terminology']['selected_terms']}")
print(f"Related Concepts: {result['knowledge_graph']['related_concepts']}")
```

### Knowledge Graph Queries

```python
# Get term hierarchy
hierarchy = await engine.get_term_hierarchy("OAuth")
print(f"Parents: {hierarchy['parents']}")
print(f"Children: {hierarchy['children']}")
print(f"Related: {hierarchy['related']}")

# Get system statistics
stats = await engine.get_terminology_stats()
print(f"Total terms indexed: {stats['terminology_index']['total_files']}")
print(f"Knowledge graph nodes: {stats['knowledge_graph']['node_count']}")
```

## Troubleshooting

### Common Issues

1. **No terms extracted**
   - Check that `terminology.enabled` is `true` in config
   - Verify the page has enough content
   - Lower `confidence_threshold` if terms are being filtered

2. **AI extraction not working**
   - Verify `OPENAI_API_KEY` is set
   - Check `use_ai_extraction` is `true`
   - System falls back to heuristics if AI unavailable

3. **Zoekt search not working**
   - Verify Zoekt server is running at configured URL
   - Check `zoekt.enabled` is `true`
   - System falls back to local search if Zoekt unavailable

4. **Knowledge graph empty**
   - Ensure `build_knowledge_graph` is `true`
   - Terms must be extracted before graph is populated
   - Check that terminology extraction succeeded

### Performance Tuning

- **Reduce `max_terms_per_page`** to speed up extraction
- **Disable AI features** (`use_ai_extraction: false`) for faster processing
- **Limit search results** with smaller `limit` parameters
- **Disable knowledge graph expansion** (`expand_related: false`) for faster search

## API Reference

### TerminologyExtractor

| Method | Description |
|--------|-------------|
| `extract_from_page(page)` | Extract terms from a ScrapedPage |

### TerminologyIndexer

| Method | Description |
|--------|-------------|
| `index_terms(terms, collection)` | Index terms for search |
| `search_terms(query, limit)` | Search indexed terms |
| `get_term_details(term_id)` | Get details for a specific term |
| `get_index_stats()` | Get index statistics |
| `delete_collection(name)` | Delete a term collection |

### TermSelector

| Method | Description |
|--------|-------------|
| `select_terms(terms, query, criteria)` | Select best terms for query |
| `get_similar_terms(target, all_terms)` | Find similar terms |

### KnowledgeGraph (Terminology Methods)

| Method | Description |
|--------|-------------|
| `add_terminology(terms)` | Add terms to graph |
| `search_terminology(query)` | Search terminology nodes |
| `get_term_hierarchy(term)` | Get term relationships |

### AgenticRAGEngine (Terminology Methods)

| Method | Description |
|--------|-------------|
| `extract_and_index_terminology(page)` | Extract and index terms |
| `terminology_aware_search(query)` | Enhanced search with terms |
| `get_term_hierarchy(term)` | Get term hierarchy |
| `get_terminology_stats()` | Get system statistics |
