# Documentation MCP Server & CLI

An advanced Model Context Protocol (MCP) server and interactive CLI that provides comprehensive documentation search with AI-powered terminology extraction, knowledge graphs, and flexible documentation loading capabilities.

## Features

### Core Capabilities
- **Interactive CLI Terminal**: Chat with documentation using natural language
- **Flexible Documentation Loading**: Load from files, URLs, or search by library name
- **AI-Powered Documentation Discovery**: Automatically find and scrape documentation sites
- **AI-Powered Terminology Extraction**: Intelligent identification of important terms and concepts
- **Knowledge Graph Integration**: Relationships between functions, concepts, and examples
- **Natural Language Responses**: Comprehensive answers combining code and explanations
- **Proactive Indexing**: Background processing for instant results

### Documentation Loading Methods
- **File Upload**: Load markdown, HTML, text, or RST files directly
- **URL Loading**: Scrape documentation from any web URL with optional link following
- **Name Search**: AI-powered search to find and load documentation by library/framework name

### Search Capabilities
- **Code Patterns**: Function definitions, syntax examples, usage patterns
- **Conceptual Understanding**: Explanations, relationships, best practices
- **Cross-Reference**: Links between related documentation
- **Context-Aware**: Tailored responses based on user's code context
- **Terminology-Aware Search**: Search using extracted terminology and knowledge graphs

## Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd documentation-mcp

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your settings
```

### Running the Server

#### MCP Server (for IDE integration)
```bash
# Start the MCP server
python src/documentation-mcp-server.py --config config/config.yaml
```

#### Interactive CLI (for terminal use)
```bash
# Run the interactive CLI
python chat.py

# Or with a custom config
python chat.py /path/to/config.yaml
```

#### CLI Commands
The CLI supports these commands:
- `/load <name>` - Load docs by library name (e.g., `/load React`)
- `/url <url>` - Load docs from URL
- `/file <path>` - Load docs from local file
- `/find <name>` - Find docs without loading
- `/terms <query>` - Search terminology
- `/term <name>` - Get term info
- `/status` - Show loaded docs
- `/clear` - Clear history
- `/help` - Show all commands

### MCP Tools
The server exposes these MCP tools:

1. **search_documentation** - Primary search with AI-enhanced results
2. **get_site_context** - Deep dive into specific documentation sites
3. **explore_related** - Recursive exploration of related topics
4. **get_examples** - Extract code examples for specific queries
5. **validate_info** - Cross-reference statements across sources
6. **load_documentation_from_url** - Load docs from a URL
7. **load_documentation_from_file** - Load docs from uploaded file
8. **load_documentation_by_name** - AI-powered search and load docs
9. **find_documentation** - Find docs without loading
10. **terminology_search** - Search with terminology awareness
11. **get_term_info** - Get term hierarchy from knowledge graph
12. **get_terminology_stats** - Get indexing statistics

## Architecture

```
documentation-mcp/
├── PROJECT.md               # Main project documentation
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── .claude/                # Claude AI configuration
├── .windsurf/              # Windsurf AI workflows
│   └── code/               # Workflow scripts
├── assets/                 # Static files and resources
│   └── file_definition.md
├── config/                 # Configuration files
│   └── config.yaml
├── docs/                   # All documentation
│   ├── README.md
│   ├── cli-implementation.md
│   ├── documentation-loader-implementation.md
│   ├── documentation-mcp-implementation.md
│   ├── refactor-best-practices.md
│   ├── terminology-system-implementation.md
│   └── zoekt-integration-plan.md
├── chat.py                 # CLI entry point
└── src/                    # All Python source code
    ├── __init__.py
    ├── agentic_rag.py      # RAG coordination engine
    ├── cache_manager.py    # Caching system
    ├── chat.py             # CLI implementation
    ├── cli.py              # CLI interface
    ├── content_processor.py # Content processing
    ├── context_builder.py  # Context building
    ├── deep_search.py      # Deep search functionality
    ├── documentation_loader.py # Documentation loading
    ├── documentation-mcp-server.py # MCP server
    ├── enhanced_search.py  # Enhanced search
    ├── server.py           # MCP server and tool registration
    ├── settings.py         # Configuration management
    ├── site_identifier.py  # Site identification
    ├── web_scraper.py      # Web scraping
    ├── point_list/         # Structured knowledge extraction
    │   ├── __init__.py
    │   ├── analyzer.py
    │   ├── builder.py
    │   └── knowledge.py
    ├── proactive/          # Background indexing
    │   ├── __init__.py
    │   ├── indexer.py
    │   └── scheduler.py
    ├── terminology/        # AI-powered terminology system
    │   ├── __init__.py
    │   ├── extractor.py
    │   ├── indexer.py
    │   └── selector.py
    └── zoekt/              # Fast code search integration
        ├── __init__.py
        ├── client.py
        ├── indexer.py
        └── search.py
```

## Configuration

Key configuration options in `config/config.yaml`:

```yaml
# Server settings
server:
  host: "localhost"
  port: 8080

# AI-powered terminology extraction
terminology:
  enabled: true
  use_ai_extraction: true
  use_ai_selection: true
  build_knowledge_graph: true

# Zoekt code search (planned)
zoekt:
  enabled: true
  server_url: "http://localhost:6070"
```

## Usage Examples

### CLI Usage

```bash
# Load React documentation by name
> /load React
ℹ Searching for 'React' documentation...
✓ Loaded 5 pages from 'React'
ℹ Extracted 67 terms

[1 docs] > How do I use hooks?
Related Terms: React Hooks, useState, useEffect
[Answer with code examples and explanations]

# Load from URL
> /url https://fastapi.tiangolo.com/
✓ Loaded 8 pages from URL
ℹ Extracted 42 terms

# Load local file
> /file ./docs/api.md
✓ Loaded file: api.md
ℹ Extracted 15 terms
```

### MCP Usage

#### Basic Search
```json
{
  "tool": "search_documentation",
  "params": {
    "query": "How to use React useState hook",
    "code_context": "function Component() { const [count, setCount] = useState(0); }"
  }
}
```

#### Load Documentation by Name
```json
{
  "tool": "load_documentation_by_name",
  "params": {
    "name": "FastAPI",
    "auto_scrape": true,
    "max_pages": 5
  }
}
```

#### Load Documentation from URL
```json
{
  "tool": "load_documentation_from_url",
  "params": {
    "url": "https://docs.python.org/3/library/asyncio.html",
    "follow_links": true
  }
}
```

#### Terminology Search
```json
{
  "tool": "terminology_search",
  "params": {
    "query": "authentication patterns",
    "use_knowledge_graph": true
  }
}
```

#### Code Examples
```json
{
  "tool": "get_examples",
  "params": {
    "query": "FastAPI routing examples",
    "language": "python"
  }
}
```

### Deep Exploration
```json
{
  "tool": "explore_related",
  "params": {
    "topic": "React hooks",
    "depth": 2
  }
}
```

## Documentation

- **[Implementation Guide](docs/documentation-mcp-implementation.md)** - Complete system documentation
- **[Terminology System](docs/terminology-system-implementation.md)** - AI-powered search details
- **[Documentation Loader](docs/documentation-loader-implementation.md)** - Flexible documentation loading
- **[CLI Implementation](docs/cli-implementation.md)** - Interactive chat terminal
- **[Refactor Best Practices](docs/refactor-best-practices.md)** - Project organization guide
- **[Zoekt Integration Plan](docs/zoekt-integration-plan.md)** - Future enhancement roadmap

## Development

### Project Structure
- **Core Components**: MCP server, RAG engine, web scraper, documentation loader
- **CLI Interface**: Interactive terminal with rich formatting and commands
- **AI Integration**: Terminology extraction, knowledge graphs, natural language generation, documentation discovery
- **Search Systems**: Text search, code search, semantic search, terminology-aware search
- **Documentation Loading**: File upload, URL scraping, AI-powered name search
- **Caching**: TTL-based caching for performance

### Key Components
- **DocumentationMCPServer**: MCP protocol server with 12 tools
- **DocumentationCLI**: Interactive chat terminal with rich output
- **DocumentationLoader**: Flexible loading (file, URL, name-based)
- **DocumentationFinder**: AI-powered documentation discovery
- **AgenticRAGEngine**: Orchestrates search and terminology extraction
- **TerminologyExtractor**: AI-powered term identification
- **KnowledgeGraph**: Relationships between terms and concepts
- **Zoekt Integration**: Fast code search (planned)

### Dependencies
- **MCP SDK**: Protocol implementation
- **Rich**: Beautiful terminal formatting for CLI
- **Async HTTP**: aiohttp for web scraping
- **AI Models**: OpenAI for natural language generation and documentation discovery
- **Embeddings**: Sentence Transformers for semantic search
- **Parsing**: BeautifulSoup for HTML processing
- **Search**: DuckDuckGo for documentation discovery

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request with documentation

## License

[Add license information here]

## Support

For issues and questions:
- Check the [documentation](docs/) for detailed guides
- Review the [configuration options](config/config.yaml)
- Check the troubleshooting section in the implementation guide
