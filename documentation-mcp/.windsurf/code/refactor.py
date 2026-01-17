#!/usr/bin/env python3
"""
Refactor/Cleanup: Organize project folder by moving coding files to appropriate directories
"""

import os
import sys
import shutil
import argparse
import re
from pathlib import Path
from datetime import datetime


# Enhanced file organization rules - more aggressive organization
ORGANIZATION_RULES = {
    # Python files - organize by type
    ".py": {
        "target": "src",
        "exclude": ["setup.py"],  # Only keep setup.py in root
        "exclude_patterns": []  # Remove server exclusions - move everything to src/
    },
    # Markdown documentation - organize by type
    ".md": {
        "target": "docs",
        "exclude": ["README.md"],  # Only keep README.md in root
        "exclude_patterns": []
    },
    # Config files
    ".yaml": {"target": "config", "exclude": [], "exclude_patterns": []},
    ".yml": {"target": "config", "exclude": [], "exclude_patterns": []},
    ".toml": {"target": "config", "exclude": [], "exclude_patterns": []},  # Move all toml files
    ".json": {"target": "config", "exclude": [], "exclude_patterns": []},  # Move all json files
    # Additional file types
    ".txt": {"target": "docs", "exclude": ["requirements.txt"], "exclude_patterns": []},
    ".sh": {"target": "scripts", "exclude": [], "exclude_patterns": []},
    ".bat": {"target": "scripts", "exclude": [], "exclude_patterns": []},
    ".sql": {"target": "scripts", "exclude": [], "exclude_patterns": []},
    # Asset files
    ".png": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".jpg": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".jpeg": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".gif": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".svg": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".ico": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".css": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".js": {"target": "assets", "exclude": [], "exclude_patterns": []},
    ".html": {"target": "assets", "exclude": [], "exclude_patterns": []},
}

# Minimal skip list - only essential system files
SKIP_ITEMS = {
    ".git", ".gitignore", ".gitattributes",
    ".windsurf", ".claude", ".vscode", ".idea",
    "node_modules", "__pycache__", ".ruff_cache",
    "venv", ".venv", "env", ".env",
    "README.md",  # Keep main README in root
    "requirements.txt",  # Keep requirements in root
    "Makefile", "Dockerfile", "docker-compose.yml",
    "LICENSE", "LICENSE.txt",
}


def matches_pattern(filename: str, patterns: list) -> bool:
    """Check if filename matches any of the glob-like patterns"""
    import fnmatch
    return any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)


def get_target_directory(file_path: Path) -> tuple[str | None, str]:
    """Determine target directory for a file. Returns (target_dir, reason)"""
    filename = file_path.name
    suffix = file_path.suffix.lower()
    
    # Check if file should be skipped
    if filename in SKIP_ITEMS:
        return None, "in skip list"
    
    # Check organization rules
    if suffix in ORGANIZATION_RULES:
        rule = ORGANIZATION_RULES[suffix]
        
        # Check exclusions
        if filename in rule["exclude"]:
            return None, "excluded by rule"
        
        if matches_pattern(filename, rule.get("exclude_patterns", [])):
            return None, "matches exclude pattern"
        
        return rule["target"], "matched rule"
    
    return None, "no matching rule"


def scan_project(project_root: Path) -> dict:
    """Scan project root and categorize files"""
    results = {
        "to_move": [],
        "skipped": [],
        "already_organized": []
    }
    
    for item in project_root.iterdir():
        # Skip directories
        if item.is_dir():
            if item.name not in SKIP_ITEMS:
                results["already_organized"].append((item.name, "directory"))
            continue
        
        target_dir, reason = get_target_directory(item)
        
        if target_dir:
            results["to_move"].append({
                "file": item,
                "target": project_root / target_dir,
                "reason": reason
            })
        else:
            results["skipped"].append((item.name, reason))
    
    return results


def update_imports_and_references(project_root: Path, moved_files: list) -> int:
    """Update import statements and file references after moving files"""
    updated_count = 0
    
    print(f"\n🔧 Updating import statements and references...")
    
    # Create mapping of old paths to new paths
    path_mappings = {}
    for old_name, target_dir in moved_files:
        old_path = project_root / old_name
        new_path = project_root / target_dir / old_name
        path_mappings[str(old_path)] = str(new_path)
    
    # Patterns to find import statements and file references
    patterns = [
        # Python imports
        r'from\s+([\'"])(.*?)\1\s+import',
        r'import\s+([\'"])(.*?)\1',
        r'from\s+(\w+)',
        r'import\s+(\w+)',
        # File paths in various contexts
        r'([\'"])([^\'"]*\.(?:py|md|yaml|yml|toml|json|txt|sh|sql))\1',
        # Relative imports
        r'from\s+\.+\s+\w+',
        r'import\s+\.+\w+',
    ]
    
    # Scan all Python files for references
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("."):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            original_content = content
            changes_made = False
            
            # Check each moved file for potential references
            for old_path, new_path in path_mappings.items():
                old_file = Path(old_path)
                new_file = Path(new_path)
                
                # Update direct file path references
                if str(old_file) in content:
                    content = content.replace(str(old_file), str(new_file))
                    changes_made = True
                
                # Update relative imports
                if old_file.stem in content:
                    # Handle module name changes
                    old_module = old_file.stem
                    new_module = f"{new_file.parent.name}.{old_file.stem}" if new_file.parent.name != "src" else old_file.stem
                    
                    # Update import statements
                    content = re.sub(
                        rf'\bimport\s+{re.escape(old_module)}\b',
                        f'import {new_module}',
                        content
                    )
                    content = re.sub(
                        rf'\bfrom\s+{re.escape(old_module)}\s+import',
                        f'from {new_module} import',
                        content
                    )
                    changes_made = True
            
            # Write back if changes were made
            if changes_made and content != original_content:
                py_file.write_text(content, encoding='utf-8')
                updated_count += 1
                print(f"  ✅ Updated: {py_file.relative_to(project_root)}")
                
        except Exception as e:
            print(f"  ⚠️  Could not update {py_file.name}: {e}")
    
    # Update configuration files that might reference moved files
    config_extensions = ['.yaml', '.yml', '.toml', '.json']
    for config_file in project_root.rglob("*"):
        if config_file.suffix in config_extensions and not config_file.name.startswith("."):
            try:
                content = config_file.read_text(encoding='utf-8')
                original_content = content
                changes_made = False
                
                for old_path, new_path in path_mappings.items():
                    if str(Path(old_path).relative_to(project_root)) in content:
                        relative_old = str(Path(old_path).relative_to(project_root))
                        relative_new = str(Path(new_path).relative_to(project_root))
                        content = content.replace(relative_old, relative_new)
                        changes_made = True
                
                if changes_made and content != original_content:
                    config_file.write_text(content, encoding='utf-8')
                    updated_count += 1
                    print(f"  ✅ Updated config: {config_file.relative_to(project_root)}")
                    
            except Exception as e:
                print(f"  ⚠️  Could not update config {config_file.name}: {e}")
    
    return updated_count


def check_for_broken_imports(project_root: Path) -> list:
    """Check for potentially broken import statements after refactoring"""
    broken_imports = []
    
    print(f"\n🔍 Checking for broken imports...")
    
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("."):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Find import statements
            import_patterns = [
                r'from\s+([\'"])(.*?)\1\s+import',
                r'import\s+([\'"])(.*?)\1',
                r'from\s+(\w+)',
                r'import\s+(\w+)',
            ]
            
            for pattern in import_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    module_name = match.group(2) if match.group(2) else match.group(1)
                    
                    # Check if it's a relative import that might be broken
                    if module_name.startswith('.') or module_name in ['chat', 'documentation_mcp_server']:
                        broken_imports.append({
                            'file': str(py_file.relative_to(project_root)),
                            'import': module_name,
                            'line': content[:match.start()].count('\n') + 1
                        })
        
        except Exception as e:
            print(f"  ⚠️  Could not check {py_file.name}: {e}")
    
    return broken_imports


def move_files(results: dict, dry_run: bool = False) -> list:
    """Move files to their target directories"""
    moved = []
    
    for item in results["to_move"]:
        source = item["file"]
        target_dir = item["target"]
        target_file = target_dir / source.name
        
        # Check if target already exists
        if target_file.exists():
            print(f"  ⚠️  Skipping {source.name}: already exists in {target_dir.name}/")
            continue
        
        if dry_run:
            print(f"  📦 Would move: {source.name} → {target_dir.name}/")
        else:
            # Create target directory if needed
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(source), str(target_file))
            print(f"  ✅ Moved: {source.name} → {target_dir.name}/")
        
        moved.append((source.name, target_dir.name))
    
    return moved


def display_structure(project_root: Path):
    """Display the current folder structure"""
    print("\n📁 Current Project Structure:")
    print("─" * 50)
    
    def display_tree(path: Path, prefix: str = "", is_last: bool = True):
        """Recursively display directory tree"""
        if path.name.startswith(".") and path.name not in [".gitignore"]:
            return
        
        # Get sorted items
        items = sorted([item for item in path.iterdir() if not item.name.startswith(".") or item.name == ".gitignore"])
        
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            current_prefix = "└── " if is_last_item else "├── "
            
            if item.is_dir():
                # Count files in directory
                file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                print(f"{prefix}{current_prefix}📂 {item.name}/ ({file_count} files)")
                
                # Recurse into subdirectory
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                display_tree(item, next_prefix, True)
            else:
                print(f"{prefix}{current_prefix}📄 {item.name}")
    
    # Display from root
    for item in sorted(project_root.iterdir()):
        if item.name.startswith(".") and item.name not in [".gitignore"]:
            continue
            
        if item.is_dir():
            file_count = sum(1 for _ in item.rglob("*") if _.is_file())
            print(f"📂 {item.name}/ ({file_count} files)")
            display_tree(item, "", True)
        else:
            print(f"📄 {item.name}")


def show_example_structure():
    """Display an example of well-organized project structure"""
    print("\n📚 Example Well-Organized Structure:")
    print("─" * 50)
    example = """
📄 README.md
📄 requirements.txt
📄 pyproject.toml
📄 Makefile
📄 .gitignore

📂 src/
├── 📄 main.py
├── 📄 server.py
├── 📄 cli.py
├── 📄 cache_manager.py
├── 📄 content_processor.py
├── 📄 documentation_loader.py
├── 📄 web_scraper.py
├── 📂 point_list/
│   ├── 📄 __init__.py
│   ├── 📄 analyzer.py
│   └── 📄 builder.py
├── 📂 proactive/
│   ├── 📄 __init__.py
│   ├── 📄 indexer.py
│   └── 📄 scheduler.py
├── 📂 zoekt/
│   ├── 📄 __init__.py
│   ├── 📄 client.py
│   └── 📄 indexer.py
└── 📂 terminology/
    ├── 📄 __init__.py
    └── 📄 selector.py

📂 docs/
├── 📄 README.md
├── 📄 api-reference.md
├── 📄 installation.md
├── 📄 usage-guide.md
├── 📄 contributing.md
└── 📄 changelog.md

📂 config/
├── 📄 config.yaml
├── 📄 settings.json
└── 📄 environment.toml

📂 scripts/
├── 📄 setup.sh
├── 📄 deploy.sh
└── 📄 migrate.sql

📂 assets/
├── 📄 logo.png
├── 📄 screenshot.jpg
├── 📄 style.css
└── 📄 script.js

📂 tests/
├── 📄 test_main.py
├── 📄 test_server.py
└── 📂 integration/
    └── 📄 test_api.py
"""
    print(example)


def main():
    parser = argparse.ArgumentParser(description="Organize project files into appropriate directories")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    parser.add_argument("--path", type=str, default=".", help="Project root path")
    parser.add_argument("--example", action="store_true", help="Show example of well-organized structure")
    args = parser.parse_args()
    
    project_root = Path(args.path).resolve()
    
    print(f"\n🔧 Enhanced Project Refactor/Cleanup")
    print(f"📍 Project: {project_root}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.example:
        show_example_structure()
        return 0
    
    if args.dry_run:
        print("🔍 Mode: DRY RUN (no files will be moved)")
    
    print("\n" + "=" * 60)
    
    # Show example first
    print("\n📚 Reference Structure:")
    show_example_structure()
    
    # Scan project
    print("\n📊 Scanning project...")
    results = scan_project(project_root)
    
    # Display what will be moved
    if results["to_move"]:
        print(f"\n📦 Files to organize ({len(results['to_move'])}):")
        moved = move_files(results, dry_run=args.dry_run)
        
        # Update imports and references if files were actually moved
        if moved and not args.dry_run:
            updated_count = update_imports_and_references(project_root, moved)
            
            # Check for broken imports
            broken_imports = check_for_broken_imports(project_root)
            
            if broken_imports:
                print(f"\n⚠️  Found {len(broken_imports)} potentially broken imports:")
                for item in broken_imports:
                    print(f"  • {item['file']}:{item['line']} - '{item['import']}'")
                print("\n💡 You may need to manually fix these imports")
            elif updated_count > 0:
                print(f"\n✅ Successfully updated {updated_count} files with new import paths")
    else:
        print("\n✨ No files need to be moved - project is already organized!")
        moved = []
    
    # Display skipped files
    if results["skipped"]:
        print(f"\n⏭️  Skipped files ({len(results['skipped'])}):")
        for name, reason in results["skipped"]:
            print(f"  • {name}: {reason}")
    
    # Display structure
    display_structure(project_root)
    
    # Summary
    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"🔍 DRY RUN COMPLETE: {len(moved)} files would be moved")
        print("💡 Run without --dry-run to apply changes")
        print("💡 Use --example to see reference structure")
    else:
        print(f"✅ REFACTOR COMPLETE: {len(moved)} files organized")
        print("💡 Your project structure now matches best practices!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
