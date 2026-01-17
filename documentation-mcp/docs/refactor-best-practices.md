# Refactor Best Practices & Common Pitfalls

## ⚠️ CRITICAL: Import Statement Updates

The most common issue with refactoring is **import statement updates failing silently**. Here's what to watch for:

### The Problem

Refactor tools often fail to properly update imports because:
- They can't parse complex import patterns
- They miss dynamic imports using strings
- They don't handle relative imports correctly
- They skip non-Python files that might contain imports

### ✅ Best Practice: Manual Verification

**ALWAYS manually verify import updates after refactoring:**

```bash
# 1. Search for old import patterns
grep -r "from chat import" src/
grep -r "import chat" src/
grep -r "from documentation_mcp_server import" src/
grep -r "import documentation_mcp_server" src/

# 2. Search for dynamic imports
grep -r "importlib.import_module" src/
grep -r "__import__" src/
grep -r "getattr.*chat" src/

# 3. Check configuration files
grep -r "chat\.py" config/
grep -r "documentation-mcp-server\.py" config/
```

### ✅ Best Practice: Test After Refactor

**Always test the project after refactoring:**

```bash
# Test entry points
python src/chat.py --help
python src/documentation-mcp-server.py --help

# Run tests if they exist
python -m pytest tests/

# Check imports work
python -c "from src.cli import DocumentationCLI; print('✓ CLI imports work')"
```

## 📁 File Organization Best Practices

### Entry Points vs Library Modules

**Entry Points (keep in root or move to src/):**
- `chat.py` - CLI entry point
- `documentation-mcp-server.py` - MCP server entry point
- `main.py` - Generic entry point
- `run.py` - Execution script

**Library Modules (must be in src/):**
- All modules that are imported by other code
- Package directories with `__init__.py`
- Utility modules
- Core functionality

### Documentation Organization

```
docs/
├── README.md                 # Overview
├── installation.md           # Setup instructions
├── usage-guide.md            # How to use
├── api-reference.md          # API docs
├── implementation/           # Implementation details
│   ├── terminology-system.md
│   ├── documentation-loader.md
│   └── cli-implementation.md
└── examples/                 # Code examples
    ├── basic-usage.py
    └── advanced-config.py
```

## 🔧 Configuration Updates

### Path References in Config Files

**Before refactoring:**
```yaml
# config/config.yaml
server:
  script: "./documentation-mcp-server.py"
  
paths:
  docs: "./docs"
  static: "./assets"
```

**After refactoring:**
```yaml
# config/config.yaml
server:
  script: "./src/documentation-mcp-server.py"
  
paths:
  docs: "./docs"
  static: "./assets"
```

### Environment Variables

```bash
# Before
export DOCS_SERVER="./documentation-mcp-server.py"

# After
export DOCS_SERVER="./src/documentation-mcp-server.py"
```

## 🚨 Common Refactor Pitfalls

### 1. Silent Import Failures

```python
# ❌ This will break after refactor
import chat  # Fails when chat.py moves to src/

# ✅ Use relative imports for modules
from . import cli

# ✅ Use absolute imports for entry points
# (Don't import entry points - run them directly)
```

### 2. Dynamic Imports

```python
# ❌ Breaks after refactor
module = importlib.import_module("chat")

# ✅ Update paths
module = importlib.import_module("src.chat")

# ✅ Better: Use configuration
MODULE_PATH = os.getenv("CHAT_MODULE", "src.chat")
module = importlib.import_module(MODULE_PATH)
```

### 3. Path References in Tests

```python
# ❌ Hardcoded paths break
def test_chat_cli():
    result = subprocess.run(["python", "chat.py", "--help"])

# ✅ Use configurable paths
CHAT_PATH = os.getenv("CHAT_PATH", "src/chat.py")
def test_chat_cli():
    result = subprocess.run(["python", CHAT_PATH, "--help"])
```

## ✅ Refactor Checklist

### Before Refactoring
- [ ] Create backup of project
- [ ] Run tests to ensure they pass
- [ ] Document current structure
- [ ] Identify entry points vs modules

### During Refactoring
- [ ] Use dry-run mode first
- [ ] Review file movements
- [ ] Check for duplicate files

### After Refactoring
- [ ] **CRITICAL: Verify all imports**
- [ ] Update documentation references
- [ ] Update configuration files
- [ ] Update scripts and entry points
- [ ] Test all entry points work
- [ ] Run full test suite
- [ ] Check for broken symlinks

## 📋 Example Refactor Commands

### Safe Refactor Workflow

```bash
# 1. Dry run to preview
python .windsurf/code/refactor.py --dry-run

# 2. Review the planned changes
# Look at what files will be moved

# 3. Run the refactor
python .windsurf/code/refactor.py

# 4. CRITICAL: Manual verification
grep -r "from chat import" src/
grep -r "import chat" src/

# 5. Update any found imports
# Manual editing required here

# 6. Test everything works
python src/chat.py --help
python src/documentation-mcp-server.py --help
```

### Import Fix Script (Example)

```python
#!/usr/bin/env python3
"""Script to fix imports after refactor"""

import os
import re
from pathlib import Path

def fix_imports(root_dir):
    """Fix common import patterns after refactor."""
    
    # Patterns to fix
    replacements = [
        (r'^from chat import', 'from src.chat import'),
        (r'^import chat$', 'import src.chat'),
        (r'^from documentation_mcp_server import', 'from src.documentation_mcp_server import'),
        (r'^import documentation_mcp_server$', 'import src.documentation_mcp_server'),
    ]
    
    for py_file in Path(root_dir).rglob("*.py"):
        content = py_file.read_text()
        modified = False
        
        for pattern, replacement in replacements:
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                modified = True
        
        if modified:
            py_file.write_text(content)
            print(f"Fixed imports in {py_file}")

if __name__ == "__main__":
    fix_imports("src")
```

## 🎯 Key Takeaways

1. **NEVER trust automatic import updates** - Always verify manually
2. **Entry points are different from modules** - Handle them separately
3. **Test after refactoring** - Ensure everything still works
4. **Document the changes** - Update all references
5. **Use dry-run mode** - Preview before applying changes

Remember: A refactor isn't complete until you've verified that imports work and the project still runs correctly!
