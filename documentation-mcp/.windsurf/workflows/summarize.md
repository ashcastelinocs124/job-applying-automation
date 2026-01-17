---
description: Summarize chat conversation with timestamp
---

# Summarize Chat Conversation Workflow

This workflow generates a comprehensive summary of the current chat conversation with Cascade agent, including a timestamp when the command is called.

## Steps

1. **Capture conversation state** - Collect all messages, context, and interaction history
2. **Generate timestamp** - Record the exact time when the summary is requested
3. **Analyze conversation content** - Extract key topics, decisions, and action items
4. **Create structured summary** - Format the information in an organized, readable format
5. **Output summary with metadata** - Present the summary with timestamp and relevant metadata

## Usage

Run this workflow when you want to:
- Document a conversation for future reference
- Create a record of decisions made during development
- Save progress before switching contexts
- Generate a summary for sharing with team members
- Create a checkpoint in a long-running conversation

## Implementation

The workflow can use the `command` script if available for programmatic summary generation:

```bash
# Execute the summary script
python .windsurf/code/command.py
```

This will:
- Generate a timestamped summary of the current conversation
- Extract key points and action items
- Include conversation metadata (duration, participants, topics)
- Format the summary in a structured JSON or markdown format
- Save the summary to the `.windsurf/summary/` folder for future reference

## Expected Output

After completion, you should see:
- **Timestamp**: Exact date and time when summary was generated
- **Conversation Overview**: Brief description of the main topics discussed
- **Key Points**: Important information and decisions made
- **Action Items**: Tasks or next steps identified
- **Technical Details**: Code changes, file modifications, or configurations
- **Context Information**: Current project state and environment details
- **Summary Statistics**: Number of messages, duration, topics covered

## Summary Format

The summary will be structured as follows:

```json
{
  "timestamp": "2026-01-04T09:42:00Z",
  "conversation_id": "session_123",
  "duration": "45 minutes",
  "topics_discussed": ["workflow creation", "project documentation"],
  "key_decisions": ["Created workflow files", "Moved to .windsurf directory"],
  "action_items": ["Test workflows", "Update documentation"],
  "technical_changes": ["Created clear.md", "Updated summarize.md"],
  "next_steps": ["Complete remaining workflows", "Test functionality"]
}
```

## Benefits

- **Context Preservation**: Maintains a record of conversations for continuity
- **Knowledge Transfer**: Enables sharing of conversation insights with others
- **Progress Tracking**: Documents development progress and decisions
- **Reference Material**: Creates searchable documentation of past interactions
