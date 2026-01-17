# Documentation Chat CLI Implementation

## Project Summary

This implementation adds an interactive CLI terminal that allows users to chat with documentation using natural language. Users can load documentation from files, URLs, or by searching for library names, then ask questions and get AI-powered answers.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI
python src/chat.py

# Or with a custom config
python src/chat.py /path/to/config.yaml
```

## Features

- **Interactive Chat** - Ask questions in natural language
- **Multiple Loading Methods** - Load docs from files, URLs, or by name
- **AI-Powered Search** - Finds documentation automatically
- **Terminology Extraction** - Extracts and indexes important terms
- **Knowledge Graph** - Builds relationships between concepts
- **Rich Terminal Output** - Syntax highlighting, tables, and panels
- **Conversation History** - Context-aware responses

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/load <name>` | Load docs by library name | `/load React` |
| `/url <url>` | Load docs from URL | `/url https://fastapi.tiangolo.com` |
| `/file <path>` | Load docs from local file | `/file ./docs/api.md` |
| `/find <name>` | Find docs without loading | `/find pandas` |
| `/terms <query>` | Search terminology | `/terms authentication` |
| `/term <name>` | Get term info | `/term useState` |
| `/status` | Show loaded docs status | `/status` |
| `/clear` | Clear conversation history | `/clear` |
| `/help` | Show all commands | `/help` |
| `/exit` | Exit the CLI | `/exit` |

## Usage Examples

### Example 1: Load and Chat with React Docs

```
> /load React
ℹ Searching for 'React' documentation...
✓ Loaded 5 pages from 'React'
ℹ Extracted 67 terms
ℹ Source: https://react.dev/

[1 docs] > How do I use hooks?

Related Terms: React Hooks, useState, useEffect, useContext

Hooks are functions that let you "hook into" React state and lifecycle 
features from function components. The most commonly used hooks are:

1. **useState** - Add state to function components
2. **useEffect** - Perform side effects
3. **useContext** - Access context values

Example:
```javascript
const [count, setCount] = useState(0);
```

Sources: https://react.dev/reference/react/hooks
```

### Example 2: Load from URL

```
> /url https://docs.python.org/3/library/asyncio.html
ℹ Loading documentation from https://docs.python.org/3/library/asyncio.html...
✓ Loaded 3 pages from URL
ℹ Extracted 42 terms

[1 docs] > What is a coroutine?

A coroutine is a specialized version of a Python generator function. 
It's defined with `async def` and can use `await` to pause execution...
```

### Example 3: Load from File

```
> /file ~/projects/myapp/docs/api.md
ℹ Loading documentation from api.md...
✓ Loaded file: api.md
ℹ Extracted 15 terms

[1 docs] > How do I authenticate?
```

### Example 4: Find Documentation First

```
> /find FastAPI
ℹ Searching for 'FastAPI' documentation...

┌─────────────────────────────────────────────────────────────────┐
│ Documentation for 'FastAPI'                                      │
├────┬──────────────────────────┬─────────────────────────┬───────┤
│ #  │ Title                    │ URL                     │ Score │
├────┼──────────────────────────┼─────────────────────────┼───────┤
│ 1  │ FastAPI                  │ https://fastapi.tiang...│ 0.95  │
│ 2  │ FastAPI Tutorial         │ https://fastapi.tiang...│ 0.88  │
│ 3  │ FastAPI - PyPI           │ https://pypi.org/proj...│ 0.72  │
└────┴──────────────────────────┴─────────────────────────┴───────┘

ℹ Use /url <url> to load a specific documentation site

> /url https://fastapi.tiangolo.com/
```

### Example 5: Explore Terminology

```
[2 docs] > /terms dependency injection

╭─────────────────── Relevant Terms ───────────────────╮
│ Depends, dependency injection, FastAPI, Dependency   │
╰──────────────────────────────────────────────────────╯

Dependency injection in FastAPI is handled through the `Depends` function...

[2 docs] > /term Depends

╭─────────────────── Term Information ─────────────────╮
│ Term: Depends                                         │
╰──────────────────────────────────────────────────────╯
  Parents: dependency injection
  Related: FastAPI, Dependency, inject
  Connections: 5
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DocumentationCLI                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ ChatSession  │  │    Rich      │  │   Command Parser     │   │
│  │  (history)   │  │  (terminal)  │  │                      │   │
│  └──────┬───────┘  └──────────────┘  └──────────┬───────────┘   │
│         │                                        │               │
│         └────────────────┬───────────────────────┘               │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   AgenticRAGEngine                        │   │
│  │  • terminology_aware_search()                             │   │
│  │  • extract_and_index_terminology()                        │   │
│  │  • get_term_hierarchy()                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 DocumentationLoader                       │   │
│  │  • load_by_name() - AI-powered search                     │   │
│  │  • load_from_url() - Direct URL scraping                  │   │
│  │  • load_from_file() - Local file loading                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
documentation-mcp/
├── src/
│   └── chat.py              # Entry point script
│   └── cli.py              # Main CLI implementation
└── requirements.txt        # Added 'rich' dependency
```

## Key Components

### ChatSession

Maintains conversation state and history.

```python
@dataclass
class ChatSession:
    messages: List[ChatMessage]      # Conversation history
    loaded_docs: List[LoadedDocumentation]  # Loaded documentation
    context: Dict[str, Any]          # Additional context
```

### DocumentationCLI

Main CLI class with command handlers.

```python
class DocumentationCLI:
    async def handle_load(name)      # /load command
    async def handle_url(url)        # /url command
    async def handle_file(path)      # /file command
    async def handle_find(name)      # /find command
    async def handle_question(q)     # Natural language questions
    async def run()                  # Main loop
```

## Dependencies

- **rich** - Beautiful terminal formatting (tables, panels, syntax highlighting)
- All existing project dependencies

## Configuration

Uses the same `config/config.yaml` as the main server. Key settings:

```yaml
ai:
  model: "gpt-3.5-turbo"  # For AI-powered responses

terminology:
  enabled: true           # Enable terminology extraction
  use_ai_extraction: true # Use AI for better term extraction
```

## Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"  # Required for AI features
```

## Tips

1. **Load multiple docs** - You can load multiple documentation sources
2. **Use /find first** - Preview documentation sites before loading
3. **Ask follow-up questions** - The CLI maintains conversation context
4. **Use /terms for specific searches** - More focused than general questions
5. **Check /status** - See what's currently loaded
