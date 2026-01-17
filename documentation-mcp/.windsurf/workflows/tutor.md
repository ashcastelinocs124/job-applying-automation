---
description: Explain code with examples, considering AI wrote the code while human provided the plan
---

# Code Tutor Workflow

This workflow provides intelligent code explanations with examples, specifically designed for scenarios where AI wrote the implementation based on human-provided plans and requirements.

## Steps

1. **Analyze code context** - Understand the code structure and purpose
2. **Identify AI vs Human contributions** - Distinguish between AI implementation and human planning
3. **Generate explanations** - Provide clear, contextual explanations with examples
4. **Show practical examples** - Demonstrate code usage with real scenarios
5. **Explain design decisions** - Clarify why certain approaches were chosen

## Usage

Run this workflow when you want to:
- Understand code that was AI-generated from human plans
- Get explanations with practical examples
- Learn the reasoning behind implementation choices
- Understand the relationship between requirements and code

## Implementation

// turbo
Execute the tutor script:

```bash
python .windsurf/code/tutor.py --file <file_path>
```

Or specify a function/class to explain:

```bash
python .windsurf/code/tutor.py --file <file_path> --function <function_name>
python .windsurf/code/tutor.py --file <file_path> --class <class_name>
```

Interactive mode for asking questions:

```bash
python .windsurf/code/tutor.py --interactive
```

## Tutor Features

### 🤖 **AI-Human Context Awareness**
- Recognizes patterns in AI-generated code
- Explains implementation decisions based on likely human requirements
- Bridges the gap between plan and execution

### 📚 **Comprehensive Explanations**
- **Purpose**: What this code accomplishes
- **Design**: Why it's structured this way
- **Usage**: How to use it with examples
- **Context**: How it fits in the larger system

### 💡 **Practical Examples**
- Real usage scenarios
- Common patterns and anti-patterns
- Integration examples
- Testing approaches

### 🔍 **Code Analysis**
- Function signatures and parameters
- Class hierarchies and relationships
- Data flow and dependencies
- Error handling patterns

## Expected Output

After completion, you should see:
- Clear explanation of the code's purpose
- Context about AI implementation vs human planning
- Practical usage examples
- Design rationale and decisions
- Integration guidance
- Potential improvements or considerations

## Example Usage

```bash
# Explain a specific function
python .windsurf/code/tutor.py --file src/zoekt/indexer.py --function prepare_for_indexing

# Explain an entire class
python .windsurf/code/tutor.py --file src/cache_manager.py --class CacheManager

# Interactive mode
python .windsurf/code/tutor.py --interactive
```

## Example Output Structure

```
🎓 Code Tutor Analysis
=====================

📋 Function: prepare_for_indexing
📁 File: src/zoekt/indexer.py
🤖 Context: AI implementation of human indexing requirements

🎯 Purpose:
[Clear explanation of what the function does]

🏗️ Design Rationale:
[Why it's implemented this way, connecting to human requirements]

💡 Usage Examples:
[Practical code examples showing how to use it]

🔗 Integration:
[How this fits into the larger system]

⚡ Performance Considerations:
[Important notes about efficiency and scaling]

🛠️ Potential Improvements:
[Suggestions for enhancement]
```
