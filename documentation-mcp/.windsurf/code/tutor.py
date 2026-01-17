#!/usr/bin/env python3
"""
Code Tutor: Explain code with examples, considering AI wrote the code while human provided the plan
"""

import os
import sys
import argparse
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class CodeTutor:
    def __init__(self):
        self.ai_patterns = [
            # Common AI-generated code patterns
            r'def\s+\w+\s*\([^)]*\)\s*->\s*\w+:',  # Type hints
            r'"""[\s\S]*?"""',  # Docstrings
            r'try:\s*\n.*?\nexcept.*?\n.*?finally',  # Comprehensive error handling
            r'if\s+__name__\s*==\s*["\']__main__["\']',  # Main guard
        ]
        
        self.human_plan_indicators = [
            # Patterns that suggest human requirements/planning
            'TODO', 'FIXME', 'NOTE', 'HACK',
            'requirements', 'specification', 'design',
            'business logic', 'user story'
        ]

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file and extract structure"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'file_path': file_path,
                'content': content,
                'ast_tree': tree,
                'classes': [],
                'functions': [],
                'imports': [],
                'docstrings': [],
                'ai_indicators': [],
                'human_indicators': []
            }
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': ast.unparse(node.returns) if node.returns else None,
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")
            
            # Detect AI vs human patterns
            for pattern in self.ai_patterns:
                if re.search(pattern, content):
                    analysis['ai_indicators'].append(pattern)
            
            for indicator in self.human_plan_indicators:
                if indicator.lower() in content.lower():
                    analysis['human_indicators'].append(indicator)
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}

    def explain_function(self, analysis: Dict, function_name: str) -> str:
        """Generate explanation for a specific function"""
        functions = [f for f in analysis['functions'] if f['name'] == function_name]
        if not functions:
            return f"❌ Function '{function_name}' not found in {analysis['file_path']}"
        
        func = functions[0]
        content_lines = analysis['content'].split('\n')
        func_lines = []
        
        # Extract function code
        start_line = func['line'] - 1
        indent_level = len(content_lines[start_line]) - len(content_lines[start_line].lstrip())
        
        for i in range(start_line, len(content_lines)):
            line = content_lines[i]
            if line.strip() == '':
                func_lines.append(line)
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and i > start_line and line.strip():
                break
            func_lines.append(line)
        
        func_code = '\n'.join(func_lines)
        
        explanation = f"""
🎓 Function Analysis: {function_name}
{'='*50}

📁 File: {analysis['file_path']}
📍 Line: {func['line']}
🤖 Context: AI implementation of human requirements

🎯 Purpose:
{self._extract_purpose(func_code, func['docstring'])}

🔧 Function Signature:
```python
{function_name}({', '.join(func['args'])}){' -> ' + func['returns'] if func['returns'] else ''}
```

📋 Parameters:
{self._explain_parameters(func['args'], func_code)}

⚡ Implementation Details:
{self._explain_implementation(func_code)}

💡 Usage Examples:
{self._generate_usage_example(function_name, func['args'], func['returns'])}

🔗 Integration:
{self._explain_integration(function_name, analysis)}

🛠️ Design Rationale:
{self._explain_design_rationale(func_code, analysis)}

⚠️ Important Notes:
{self._extract_important_notes(func_code)}
"""
        return explanation

    def explain_class(self, analysis: Dict, class_name: str) -> str:
        """Generate explanation for a specific class"""
        classes = [c for c in analysis['classes'] if c['name'] == class_name]
        if not classes:
            return f"❌ Class '{class_name}' not found in {analysis['file_path']}"
        
        cls = classes[0]
        
        explanation = f"""
🎓 Class Analysis: {class_name}
{'='*50}

📁 File: {analysis['file_path']}
📍 Line: {cls['line']}
🤖 Context: AI implementation of human requirements

🎯 Purpose:
{self._extract_purpose_from_class(cls)}

🏗️ Class Structure:
- Base Classes: {', '.join(cls['bases']) if cls['bases'] else 'None'}
- Methods: {len(cls['methods'])} methods
{self._list_methods(cls['methods'])}

💡 Usage Examples:
{self._generate_class_usage_example(class_name, cls['methods'])}

🔗 Integration:
{self._explain_class_integration(class_name, analysis)}

🛠️ Design Rationale:
{self._explain_class_design_rationale(cls, analysis)}

⚠️ Important Notes:
{self._extract_class_notes(cls, analysis)}
"""
        return explanation

    def explain_file(self, analysis: Dict) -> str:
        """Generate explanation for the entire file"""
        return f"""
🎓 File Analysis: {analysis['file_path'].name}
{'='*50}

📁 Path: {analysis['file_path'].relative_to(Path.cwd())}
🤖 Context: AI implementation of human requirements

📊 File Overview:
- Classes: {len(analysis['classes'])}
- Functions: {len(analysis['functions'])}
- Imports: {len(analysis['imports'])}

🏗️ Structure:
{self._list_file_structure(analysis)}

🎯 Purpose:
{self._extract_file_purpose(analysis)}

🤖 AI Implementation Patterns:
{self._explain_ai_patterns(analysis['ai_indicators'])}

👤 Human Planning Indicators:
{self._explain_human_indicators(analysis['human_indicators'])}

💡 Key Components:
{self._highlight_key_components(analysis)}

🔗 Integration:
{self._explain_file_integration(analysis)}

🛠️ Design Rationale:
{self._explain_file_design_rationale(analysis)}
"""

    def _extract_purpose(self, code: str, docstring: Optional[str]) -> str:
        """Extract the purpose of a function from its code and docstring"""
        if docstring:
            return docstring.strip()
        
        # Try to infer purpose from code
        lines = code.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                return line.strip()[1:].strip()
        
        return "Purpose not clearly documented - AI implemented based on requirements."

    def _explain_parameters(self, args: List[str], code: str) -> str:
        """Explain function parameters"""
        explanations = []
        for arg in args:
            # Look for type hints or parameter descriptions
            param_info = f"  - `{arg}`: Parameter"
            explanations.append(param_info)
        
        return '\n'.join(explanations) if explanations else "  No parameters"

    def _explain_implementation(self, code: str) -> str:
        """Explain the implementation approach"""
        if 'try:' in code and 'except' in code:
            return "  • Includes comprehensive error handling\n  • Follows Python best practices for exception management"
        
        if 'return' in code:
            return "  • Returns processed results\n  • Implements data transformation logic"
        
        return "  • Implements core business logic as specified in requirements"

    def _generate_usage_example(self, func_name: str, args: List[str], returns: Optional[str]) -> str:
        """Generate practical usage examples"""
        example_args = []
        for arg in args:
            if 'path' in arg.lower():
                example_args.append(f'"/path/to/file"')
            elif 'name' in arg.lower():
                example_args.append('"example_name"')
            elif 'data' in arg.lower():
                example_args.append('{}')
            else:
                example_args.append('None')
        
        example = f"""```python
# Basic usage
result = {func_name}({', '.join(example_args)})

# In context
try:
    result = {func_name}({', '.join(example_args)})
    print(f"Success: {{result}}")
except Exception as e:
    print(f"Error: {{e}}")
```"""
        return example

    def _explain_integration(self, func_name: str, analysis: Dict) -> str:
        """Explain how the function integrates with the system"""
        similar_functions = [f['name'] for f in analysis['functions'] 
                           if f['name'] != func_name and 
                           any(word in f['name'] for word in func_name.split('_'))]
        
        if similar_functions:
            return f"  • Works with: {', '.join(similar_functions)}\n  • Part of the {func_name.split('_')[0]} module"
        
        return f"  • Standalone function in {analysis['file_path'].name}"

    def _explain_design_rationale(self, code: str, analysis: Dict) -> str:
        """Explain why the code was designed this way"""
        rationale = []
        
        if 'def ' in code and '->' in code:
            rationale.append("  • Uses type hints for better code clarity and IDE support")
        
        if '"""' in code:
            rationale.append("  • Includes comprehensive docstrings for documentation")
        
        if 'try:' in code:
            rationale.append("  • Implements robust error handling as per requirements")
        
        if analysis['ai_indicators']:
            rationale.append("  • Follows AI best practices for code structure")
        
        return '\n'.join(rationale) if rationale else "  • Designed to meet specified requirements"

    def _extract_important_notes(self, code: str) -> str:
        """Extract important notes and warnings"""
        notes = []
        
        if 'TODO' in code or 'FIXME' in code:
            notes.append("  • Contains TODO/FIXME comments that need attention")
        
        if 'deprecated' in code.lower():
            notes.append("  • May contain deprecated functionality")
        
        if 'import os' in code or 'import sys' in code:
            notes.append("  • Uses system-level imports - ensure compatibility")
        
        return '\n'.join(notes) if notes else "  • No special considerations noted"

    def _extract_purpose_from_class(self, cls: Dict) -> str:
        """Extract class purpose"""
        if cls['docstring']:
            return cls['docstring'].strip()
        
        return f"Implements {cls['name']} functionality as specified in requirements."

    def _list_methods(self, methods: List[str]) -> str:
        """List class methods"""
        if not methods:
            return "  No methods"
        
        method_list = []
        for method in methods[:5]:  # Show first 5 methods
            method_list.append(f"  - {method}()")
        
        if len(methods) > 5:
            method_list.append(f"  ... and {len(methods) - 5} more methods")
        
        return '\n'.join(method_list)

    def _generate_class_usage_example(self, class_name: str, methods: List[str]) -> str:
        """Generate class usage examples"""
        init_method = '__init__' if '__init__' in methods else None
        example_methods = [m for m in methods if not m.startswith('_')][:3]
        
        example = f"""```python
# Initialize the class
instance = {class_name}()

# Use methods
"""
        for method in example_methods:
            example += f"result = instance.{method}()\n"
        
        example += "```"
        return example

    def _explain_class_integration(self, class_name: str, analysis: Dict) -> str:
        """Explain class integration"""
        return f"  • Core class in {analysis['file_path'].name}\n  • Likely used by other components in the system"

    def _explain_class_design_rationale(self, cls: Dict, analysis: Dict) -> str:
        """Explain class design rationale"""
        rationale = []
        
        if cls['bases']:
            rationale.append(f"  • Inherits from {', '.join(cls['bases'])} for code reuse")
        
        if len(cls['methods']) > 5:
            rationale.append("  • Comprehensive class with multiple responsibilities")
        
        if cls['docstring']:
            rationale.append("  • Well-documented class following best practices")
        
        return '\n'.join(rationale) if rationale else "  • Designed to meet specified requirements"

    def _extract_class_notes(self, cls: Dict, analysis: Dict) -> str:
        """Extract class-specific notes"""
        notes = []
        
        if not cls['docstring']:
            notes.append("  • Missing class docstring - consider adding documentation")
        
        if len(cls['methods']) == 0:
            notes.append("  • No methods defined - may be a base class or placeholder")
        
        return '\n'.join(notes) if notes else "  • No special considerations noted"

    def _list_file_structure(self, analysis: Dict) -> str:
        """List file structure"""
        structure = []
        
        if analysis['classes']:
            structure.append(f"📂 Classes ({len(analysis['classes'])}):")
            for cls in analysis['classes'][:3]:
                structure.append(f"  - {cls['name']}")
        
        if analysis['functions']:
            structure.append(f"🔧 Functions ({len(analysis['functions'])}):")
            for func in analysis['functions'][:3]:
                structure.append(f"  - {func['name']}()")
        
        return '\n'.join(structure)

    def _extract_file_purpose(self, analysis: Dict) -> str:
        """Extract overall file purpose"""
        filename = analysis['file_path'].name.lower()
        
        if 'indexer' in filename:
            return "Handles indexing and search functionality for documentation"
        elif 'cache' in filename:
            return "Manages caching operations for performance optimization"
        elif 'loader' in filename:
            return "Handles loading and processing of external data"
        elif 'server' in filename:
            return "Implements server functionality and API endpoints"
        else:
            return f"Implements {analysis['file_path'].stem} functionality as per requirements"

    def _explain_ai_patterns(self, indicators: List[str]) -> str:
        """Explain AI implementation patterns"""
        if not indicators:
            return "  • Standard implementation approach"
        
        return f"  • Uses {len(indicators)} AI best practices:\n" + '\n'.join(f"    - {pattern}" for pattern in indicators[:3])

    def _explain_human_indicators(self, indicators: List[str]) -> str:
        """Explain human planning indicators"""
        if not indicators:
            return "  • No explicit human planning indicators found"
        
        return f"  • Contains {len(indicators)} human planning elements:\n" + '\n'.join(f"    - {indicator}" for indicator in indicators)

    def _highlight_key_components(self, analysis: Dict) -> str:
        """Highlight key components in the file"""
        components = []
        
        # Find most important classes/functions
        if analysis['classes']:
            main_class = max(analysis['classes'], key=lambda c: len(c['methods']))
            components.append(f"  • {main_class['name']} - Main class with {len(main_class['methods'])} methods")
        
        if analysis['functions']:
            main_func = max(analysis['functions'], key=lambda f: len(f['args']))
            components.append(f"  • {main_func['name']} - Key function with {len(main_func['args'])} parameters")
        
        return '\n'.join(components) if components else "  • Standard module structure"

    def _explain_file_integration(self, analysis: Dict) -> str:
        """Explain file integration"""
        imports = analysis['imports']
        
        if 'os' in imports or 'sys' in imports:
            return "  • System-level integration\n  • Interacts with operating system"
        
        if any('http' in imp or 'request' in imp for imp in imports):
            return "  • Network/HTTP integration\n  • Communicates with external services"
        
        return "  • Module-level integration within the system"

    def _explain_file_design_rationale(self, analysis: Dict) -> str:
        """Explain file design rationale"""
        rationale = []
        
        if len(analysis['classes']) > 0 and len(analysis['functions']) > 0:
            rationale.append("  • Mixed architecture with both classes and functions")
        
        if len(analysis['imports']) > 5:
            rationale.append("  • High connectivity with other modules")
        
        if any('__' in f['name'] for f in analysis['functions']):
            rationale.append("  • Contains private methods for internal operations")
        
        return '\n'.join(rationale) if rationale else "  • Designed to meet specified requirements"

    def interactive_mode(self):
        """Run tutor in interactive mode"""
        print("🎓 Code Tutor - Interactive Mode")
        print("=" * 40)
        print("Ask me about any code in your project!")
        print("Type 'quit' to exit, 'help' for commands")
        print()
        
        while True:
            try:
                user_input = input("🤔 What would you like to know? ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print("""
Available commands:
- explain file <path> - Explain entire file
- explain function <file> <name> - Explain specific function
- explain class <file> <name> - Explain specific class
- list files - Show all Python files
- help - Show this help
- quit - Exit tutor
""")
                    continue
                
                # Parse commands
                parts = user_input.split()
                if len(parts) >= 3 and parts[0] == 'explain' and parts[1] == 'file':
                    file_path = Path(' '.join(parts[2:]))
                    if file_path.exists():
                        analysis = self.analyze_file(file_path)
                        if 'error' not in analysis:
                            print(self.explain_file(analysis))
                        else:
                            print(f"❌ Error: {analysis['error']}")
                    else:
                        print(f"❌ File not found: {file_path}")
                
                elif len(parts) >= 4 and parts[0] == 'explain' and parts[1] == 'function':
                    file_path = Path(parts[2])
                    func_name = parts[3]
                    if file_path.exists():
                        analysis = self.analyze_file(file_path)
                        if 'error' not in analysis:
                            print(self.explain_function(analysis, func_name))
                        else:
                            print(f"❌ Error: {analysis['error']}")
                    else:
                        print(f"❌ File not found: {file_path}")
                
                else:
                    print("🤷 I don't understand. Type 'help' for commands.")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Code Tutor - Explain code with examples")
    parser.add_argument("--file", type=str, help="File to analyze")
    parser.add_argument("--function", type=str, help="Specific function to explain")
    parser.add_argument("--class", type=str, dest="class_name", help="Specific class to explain")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--list-files", action="store_true", help="List all Python files")
    
    args = parser.parse_args()
    
    tutor = CodeTutor()
    
    if args.interactive:
        tutor.interactive_mode()
        return 0
    
    if args.list_files:
        print("📁 Python files in project:")
        for py_file in Path('.').rglob('*.py'):
            if not py_file.name.startswith('.'):
                print(f"  📄 {py_file}")
        return 0
    
    if not args.file:
        print("❌ Please specify a file with --file or use --interactive mode")
        return 1
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 1
    
    analysis = tutor.analyze_file(file_path)
    if 'error' in analysis:
        print(f"❌ Error analyzing file: {analysis['error']}")
        return 1
    
    if args.function:
        print(tutor.explain_function(analysis, args.function))
    elif args.class_name:
        print(tutor.explain_class(analysis, args.class_name))
    else:
        print(tutor.explain_file(analysis))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
