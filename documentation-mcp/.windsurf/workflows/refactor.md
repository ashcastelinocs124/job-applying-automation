---
description: Organize and clean up project folder by moving coding files to appropriate directories
---

# Enhanced Refactor/Cleanup Workflow

This workflow aggressively organizes the project folder by moving coding files to appropriate directories, making it easier to identify and navigate the codebase. It follows best practices for Python project structure.

## Steps

1. **Show reference structure** - Display example of well-organized project
2. **Analyze current structure** - Scan the project root for files that should be organized
3. **Identify file types** - Categorize files by type (Python, Markdown, Config, Assets, etc.)
4. **Move files to appropriate folders** - Relocate files to their proper directories
5. **Update import statements** - Automatically fix import statements and file references
6. **Check for broken imports** - Identify any imports that need manual attention
7. **Display organized structure** - Show the new folder structure with tree view

## Usage

Run this workflow when you want to:
- Clean up a cluttered project root
- Organize files into logical directories following Python best practices
- Make the project structure easier to navigate and maintain
- Prepare the project for better development workflow

## Implementation

// turbo
Execute the refactor script:

```bash
python .windsurf/code/refactor.py
```

Or run with dry-run mode first to preview changes:

```bash
python .windsurf/code/refactor.py --dry-run
```

To see the reference structure example:

```bash
python .windsurf/code/refactor.py --example
```

## Enhanced File Organization Rules

| File Type | Target Directory | Notes |
|-----------|------------------|-------|
| **Python files** (`.py`) | `src/` | All Python code except `setup.py` |
| **Documentation** (`.md`) | `docs/` | All markdown except `README.md` |
| **Configuration** (`.yaml`, `.yml`, `.toml`, `.json`) | `config/` | All config files |
| **Scripts** (`.sh`, `.bat`, `.sql`) | `scripts/` | Shell and utility scripts |
| **Assets** (`.png`, `.jpg`, `.css`, `.js`, `.html`) | `assets/` | Static files and media |
| **Text files** (`.txt`) | `docs/` | Text files except `requirements.txt` |

## Files Kept in Root

Only essential files remain in the project root:
- `README.md` - Main project documentation
- `requirements.txt` - Python dependencies  
- `setup.py` - Package setup script
- `Makefile` - Build automation
- `Dockerfile` - Container configuration
- `LICENSE` - License file
- `.gitignore` - Git ignore rules

## Expected Output

After completion, you should see:
- Reference structure example for comparison
- List of files that were moved with their destinations
- **Import updates performed** - Number of files updated with new import paths
- **⚠️ BROKEN IMPORT WARNINGS** - Any imports that need manual fixing
- Visual tree structure of the organized project
- Any files that were skipped (with reason)
- Confirmation of successful organization
- Summary showing before/after state

## ⚠️ CRITICAL: Post-Refactor Checklist

### REQUIRED After Every Refactor:

1. **Manual Import Verification**
   ```bash
   grep -r "from chat import" src/
   grep -r "import chat" src/
   grep -r "from documentation_mcp_server import" src/
   grep -r "import documentation_mcp_server" src/
   ```

2. **Test Entry Points**
   ```bash
   python src/chat.py --help
   python src/documentation-mcp-server.py --help
   ```

3. **Update Documentation References**
   - Update `README.md` with new paths
   - Update `docs/` files with new executable paths
   - Update any scripts or configuration files

4. **Run Full Test Suite**
   ```bash
   python -m pytest tests/  # If tests exist
   ```

### Common Issues to Fix:
- Entry point paths in documentation
- Configuration file paths
- Script references
- Import statements that weren't auto-updated

## Import Statement Updates

The refactor automatically handles:

✅ **Python Import Statements**
- `import module_name` → `import folder.module_name`
- `from module_name import something` → `from folder.module_name import something`

⚠️ **CRITICAL: Manual Verification Required**
- **NEVER trust automatic import updates** - They often fail silently
- **ALWAYS manually verify imports after refactoring**
- **Test that the project still runs after refactoring**

### Manual Verification Steps (REQUIRED):
```bash
# 1. Search for old import patterns
grep -r "from chat import" src/
grep -r "import chat" src/
grep -r "from documentation_mcp_server import" src/
grep -r "import documentation_mcp_server" src/

# 2. Search for dynamic imports
grep -r "importlib.import_module" src/
grep -r "__import__" src/

# 3. Test entry points work
python src/chat.py --help
python src/documentation-mcp-server.py --help
```

### Common Import Update Failures:
- Complex relative imports (`.module`, `..module`)
- Dynamic imports using strings
- Conditional imports
- Import statements in non-Python files
- Entry points that are imported (should be run directly)

✅ **File Path References**
- Updates absolute file paths in configuration files
- Updates relative paths in documentation
- Handles path references in scripts and utilities

✅ **Configuration Files**
- Updates paths in `.yaml`, `.yml`, `.toml`, `.json` files
- Maintains relative path structure where appropriate

## Example Before/After

**Before:**
```
📄 chat.py
📄 cli-implementation.md
📄 documentation-mcp-server.py
📄 terminology-system-implementation.md
📄 zoekt-integration-plan.md
📄 src/
📄 docs/
📄 config/
```

**After:**
```
📄 README.md
📄 requirements.txt
📄 .gitignore

📂 src/
├── 📄 chat.py
├── 📄 documentation-mcp-server.py
└── 📂 [existing modules]

📂 docs/
├── 📄 cli-implementation.md
├── 📄 terminology-system-implementation.md
├── 📄 zoekt-integration-plan.md
└── 📂 [existing docs]

📂 config/
└── 📂 [existing config]
```

**Import Updates Example:**
```python
# Before refactoring
import chat
from documentation_mcp_server import MCPServer

# After refactoring (automatically updated)
from src.chat import chat
from src.documentation_mcp_server import MCPServer
```
