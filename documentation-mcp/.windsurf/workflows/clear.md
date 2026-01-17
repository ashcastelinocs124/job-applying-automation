---
description: Clear chat conversation context with Cascade agent
---

# Clear Chat Conversation Workflow

This workflow clears the chat conversation context with Cascade agent, providing a fresh start for new conversations.

## Steps

1. **Execute clear script** - Run the clear.py script to remove conversation history
2. **Clear context files** - Remove stored conversation data and cache
3. **Create clear marker** - Add timestamp marker for when clear was performed
4. **Confirm clearance** - Verify that context has been successfully cleared

## Usage

Run this workflow when you want to:
- Start a fresh conversation without previous context
- Clear sensitive information from chat history
- Reset conversation state for testing
- Begin a new topic without previous context influence

## Implementation

Execute the clear script:

```bash
# Execute the clear script
python .windsurf/code/clear.py
```

This will:
- Clear conversation history files
- Remove context cache
- Create a timestamp marker
- Confirm successful clearance
- Preserve system configuration and user preferences
- Return a ready state for new conversation

## Expected Output

After completion, you should see:
- Confirmation that context has been cleared
- Timestamp of the clearance operation
- Ready state for new conversation
- Any preserved configuration information
