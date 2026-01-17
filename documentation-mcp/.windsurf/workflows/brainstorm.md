---
description: Brainstorm ideas with the user through collaborative discussion before creating a concrete implementation plan
---

# Brainstorm Workflow

This workflow enables collaborative brainstorming sessions where we explore ideas, discuss approaches, and iterate on concepts before committing to a specific implementation plan.

## When to Use This Workflow

Use this workflow when you want to:
- Explore multiple approaches to a problem
- Discuss system architecture options
- Brainstorm solutions for bugs or issues
- Evaluate different technologies or frameworks
- Refine requirements and constraints
- Iterate on ideas before implementation

## Brainstorming Process

### 1. Initial Idea Exploration
- Listen carefully to the user's initial request or idea
- Ask clarifying questions to understand:
  - Core problem or goal
  - Constraints and requirements
  - Success criteria
  - Available resources or technologies

### 2. Generate Multiple Options
- Present 2-4 different approaches when applicable
- For each option, discuss:
  - Pros and benefits
  - Cons and trade-offs
  - Technical considerations
  - Implementation complexity
  - Time and resource requirements

### 3. Collaborative Discussion
- Encourage user feedback on presented options
- Refine ideas based on user input
- Explore hybrid approaches if needed
- Address concerns and questions
- Iterate on concepts until alignment is reached

### 4. Convergence to Plan
- Once both parties agree on a direction:
  - Summarize the agreed approach
  - Identify key components and steps
  - Note any remaining decisions or research needed
  - Transition to the planning phase

## Brainstorming Guidelines

### For the Assistant:
- Never immediately agree to the first suggestion
- Always explore alternatives and trade-offs
- Ask "what if" questions to uncover hidden requirements
- Be honest about limitations and risks
- Encourage creative thinking while staying practical
- Use examples and analogies to clarify complex concepts

### For the User:
- Be open to different approaches
- Share constraints and preferences early
- Ask questions about unfamiliar concepts
- Provide honest feedback on suggestions
- Consider long-term implications

## Transition Signals

The brainstorming phase continues until you hear phrases like:
- "Let's go with that approach"
- "I like option X best"
- "That makes sense, let's proceed"
- "Can we create a plan for that?"

## Example Brainstorming Sessions

### Bug Fix Brainstorming
**User**: "I have a memory leak in my Python application"
**Assistant**: "Interesting! Memory leaks can have several causes. Let's explore:
1. Circular references between objects
2. Unclosed file handles or network connections  
3. Large objects not being garbage collected
4. Caching issues

What kind of application is this? Are you seeing memory usage grow over time, or does it spike during specific operations?"

### Architecture Brainstorming
**User**: "I need to build a real-time chat application"
**Assistant**: "Great! For real-time chat, we have several architectural options:
1. WebSocket-based with Redis pub/sub
2. Server-sent events with long polling fallback
3. GraphQL subscriptions
4. WebRTC for peer-to-peer

What's your expected user scale? Do you need message persistence, file sharing, or other features?"

## Output

The goal is to exit brainstorming with:
- Clear understanding of the problem
- Agreed-upon approach or direction
- Identified key components and considerations
- Readiness to move to detailed planning phase

This workflow ensures we explore ideas thoroughly before committing to implementation, leading to better solutions and fewer surprises during development.
