---
description: Generate debugging reports for Claude Code with model recommendations
---

# Debug Report Generation Workflow

This workflow analyzes the chat conversation to identify debugging issues and generates a comprehensive report for Claude Code, including recommendations for which Anthropic model to use for resolution.

## Steps

1. **Analyze chat conversation** - Scan the conversation for debugging issues, errors, and problems discussed
2. **Identify debugging patterns** - Extract common issues, error messages, and troubleshooting attempts
3. **Categorize issues by severity** - Classify problems as critical, major, or minor based on impact
4. **Generate technical report** - Create a detailed debugging report with context and solutions
5. **Recommend Anthropic model** - Suggest the best Anthropic model for each type of issue
6. **Format for Claude Code** - Structure the report for optimal processing by Claude Code

## Usage

Run this workflow when you want to:
- Document debugging issues from a conversation
- Create a report for escalation to Claude Code
- Get model recommendations for specific problem types
- Transfer debugging context to another AI assistant
- Create a comprehensive issue analysis for team review

## Implementation

The workflow can use the `debug` script if available for programmatic report generation:

```bash
# Execute the debug script with issue description
python .windsurf/code/debug.py
```

This will:
- Scan the conversation for technical problems and errors
- Extract error messages, stack traces, and failed attempts
- Analyze the complexity and nature of each issue
- Generate a structured report with technical details
- Recommend appropriate Anthropic models for resolution

## Anthropic Model Recommendations

Based on issue type and complexity:

### Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Best for**: Complex debugging, code analysis, architectural issues
- **Use cases**: Multi-file problems, system architecture, performance optimization
- **Strengths**: Advanced reasoning, large context window, detailed analysis

### Claude 3.5 Haiku (claude-3-5-haiku-20241022)
- **Best for**: Quick fixes, simple syntax errors, straightforward issues
- **Use cases**: Syntax errors, import issues, basic configuration problems
- **Strengths**: Fast response, cost-effective, simple problem resolution

### Claude 3 Opus (claude-3-opus-20240229)
- **Best for**: Critical production issues, complex system failures
- **Use cases**: Production outages, critical bugs, system-wide failures
- **Strengths**: Highest accuracy, deep technical expertise, comprehensive analysis

## Expected Output

After completion, you should see:

### Debug Report Structure
```json
{
  "timestamp": "2026-01-04T09:44:00Z",
  "report_id": "debug_report_001",
  "conversation_analysis": {
    "total_messages": 25,
    "debugging_topics": ["MCP connection", "workflow creation", "file permissions"],
    "error_count": 3,
    "severity_distribution": {
      "critical": 0,
      "major": 2,
      "minor": 1
    }
  },
  "identified_issues": [
    {
      "issue_id": "issue_001",
      "description": "MCP server connection timeout",
      "severity": "major",
      "error_messages": ["Connection refused", "Timeout after 30s"],
      "context": "Occurs during server startup",
      "recommended_model": "claude-3-5-sonnet-20241022",
      "reasoning": "Complex networking issue requiring detailed analysis"
    }
  ],
  "claude_code_instructions": {
    "primary_model": "claude-3-5-sonnet-20241022",
    "fallback_model": "claude-3-5-haiku-20241022",
    "context_requirements": "Full conversation history, error logs, system configuration",
    "expected_resolution_time": "15-30 minutes"
  },
  "escalation_priority": "medium"
}
```

## Report Sections

### 1. Executive Summary
- Overview of debugging issues found
- Severity assessment and impact analysis
- Recommended immediate actions

### 2. Technical Analysis
- Detailed breakdown of each issue
- Error messages and stack traces
- System context and environment details

### 3. Model Recommendations
- Primary Anthropic model suggestion
- Fallback options for different scenarios
- Reasoning for model selection

### 4. Claude Code Instructions
- Specific prompts and context to provide
- Expected resolution approach
- Success criteria and verification steps

## Benefits

- **Efficient Escalation**: Provides Claude Code with optimal context for resolution
- **Model Optimization**: Recommends the most cost-effective and capable Anthropic model
- **Context Preservation**: Maintains full debugging context across AI assistants
- **Faster Resolution**: Pre-analyzes issues to accelerate Claude Code's response time
- **Cost Management**: Avoids overusing expensive models for simple issues

## Integration with Claude Code

The generated report is formatted to be easily consumed by Claude Code:
- Structured JSON format for programmatic processing
- Clear issue descriptions with technical details
- Specific model recommendations with reasoning
- Actionable instructions for resolution
