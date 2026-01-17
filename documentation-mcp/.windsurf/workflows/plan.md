---
description: Generate comprehensive coding plans for AI agents like Claude Code and Codex
---

# Coding Plan Generation Workflow

This workflow analyzes a coding query and generates a comprehensive implementation plan for AI agents like Claude Code and Codex, including architecture, technical definitions, and step-by-step instructions.

## Steps

1. **Analyze the coding query** - Parse the user's request to understand requirements, scope, and constraints
2. **Define technical architecture** - Design system architecture and component structure
3. **Identify technical terms** - Extract and define key technical concepts and terminology
4. **Create implementation plan** - Generate detailed, step-by-step implementation roadmap
5. **Specify dependencies** - List required packages, tools, and external services
6. **Define testing strategy** - Outline verification and testing approaches
7. **Generate agent instructions** - Create specific prompts and context for AI agents

## Usage

Run this workflow when you want to:
- Create a structured plan for complex coding projects
- Generate comprehensive specifications for AI coding assistants
- Define architecture and technical requirements upfront
- Provide clear implementation roadmaps for development teams
- Ensure consistent terminology and technical understanding

## Implementation

Provide a coding query when executing this workflow. The workflow will:

```bash
# Execute the plan script with query
python .windsurf/code/plan.py "your coding query here"
```

This will:
- Analyze the coding requirements and constraints
- Design appropriate system architecture
- Define all technical terms and concepts
- Create detailed implementation steps
- Specify dependencies and tools needed
- Generate agent-specific instructions
- Output a comprehensive plan document

## Plan Structure

The generated plan includes these sections:

### 1. Executive Summary
- **Project Overview**: Brief description of what will be built
- **Primary Goals**: Main objectives and success criteria
- **Scope Definition**: What's included and excluded
- **Estimated Complexity**: Assessment of implementation difficulty

### 2. Technical Architecture
- **System Design**: High-level architecture diagram and description
- **Component Breakdown**: Individual components and their responsibilities
- **Data Flow**: How data moves through the system
- **Integration Points**: External systems and APIs
- **Technology Stack**: Recommended technologies and frameworks

### 3. Technical Terms & Definitions
- **Key Concepts**: Important technical terms used in the project
- **Domain Terminology**: Specific domain vocabulary and definitions
- **Acronyms & Abbreviations**: Technical shorthand and their meanings
- **Context Definitions**: How terms apply to this specific project

### 4. Implementation Plan
- **Phase 1: Foundation**: Setup, configuration, and basic structure
- **Phase 2: Core Features**: Main functionality implementation
- **Phase 3: Integration**: Connecting components and external systems
- **Phase 4: Refinement**: Optimization, testing, and documentation
- **Dependencies**: Order of operations and prerequisites

### 5. File Structure
```
project-root/
├── src/
│   ├── core/
│   ├── components/
│   ├── utils/
│   └── tests/
├── docs/
├── config/
├── scripts/
└── README.md
```

### 6. Dependencies & Tools
- **Required Packages**: List of npm/pip packages with versions
- **Development Tools**: Build tools, linters, testing frameworks
- **External Services**: APIs, databases, cloud services
- **System Requirements**: Minimum system specifications

### 7. Testing Strategy
- **Unit Tests**: Component-level testing approach
- **Integration Tests**: System interaction testing
- **End-to-End Tests**: Full workflow validation
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability and permission testing

### 8. AI Agent Instructions

#### For Claude Code
- **Recommended Model**: claude-3-5-sonnet-20241022 for complex projects
- **Context Requirements**: Full plan document, existing codebase, system specifications
- **Specific Prompts**: Tailored prompts for each implementation phase
- **Verification Steps**: How to validate each component

#### For Codex/OpenAI
- **Recommended Model**: GPT-4 for complex architecture, GPT-3.5 for simple components
- **Prompt Engineering**: Specific prompt templates for different code types
- **Code Review Steps**: How to validate generated code
- **Integration Guidelines**: How to combine multiple code generations

## Expected Output

After completion, you should see a comprehensive plan document with:

### Plan Document Structure
```markdown
# Project Implementation Plan

## Executive Summary
[Overview and goals]

## Technical Architecture
[System design and components]

## Technical Definitions
[Key terms and concepts]

## Implementation Steps
[Detailed roadmap]

## File Structure
[Complete directory layout]

## Dependencies
[Required packages and tools]

## Testing Strategy
[Verification approach]

## AI Agent Instructions
[Specific prompts and guidelines]
```

### JSON Output for Programmatic Use
```json
{
  "plan_id": "plan_001",
  "timestamp": "2026-01-08T10:28:00Z",
  "query": "user's coding query",
  "complexity": "medium",
  "estimated_time": "2-4 hours",
  "architecture": {
    "type": "microservices",
    "components": ["api", "database", "frontend"],
    "technologies": ["React", "Node.js", "PostgreSQL"]
  },
  "phases": [
    {
      "phase": 1,
      "title": "Foundation Setup",
      "steps": ["Initialize project", "Setup database", "Create basic API"]
    }
  ],
  "agent_instructions": {
    "claude_code": {
      "model": "claude-3-5-sonnet-20241022",
      "prompts": ["Specific prompts for each phase"],
      "context_requirements": ["Full plan", "Existing codebase"]
    },
    "codex": {
      "model": "gpt-4",
      "prompt_templates": ["Templates for different code types"],
      "validation_steps": ["Code review checklist"]
    }
  }
}
```

## Benefits

- **Clarity**: Provides clear, structured implementation guidance
- **Consistency**: Ensures consistent terminology and architecture understanding
- **Efficiency**: Reduces ambiguity and back-and-forth with AI agents
- **Quality**: Includes testing and verification strategies
- **Flexibility**: Adaptable to different AI agents and coding styles
- **Documentation**: Creates comprehensive project documentation

## Integration with AI Agents

The generated plan is optimized for:
- **Claude Code**: Structured prompts that leverage Claude's analytical capabilities
- **Codex**: Specific code generation templates and validation steps
- **Other Agents**: Generic plan format that can be adapted for any AI coding assistant

## Best Practices

- **Review Before Implementation**: Always review the generated plan before starting
- **Iterative Refinement**: Update the plan as requirements evolve
- **Team Alignment**: Share the plan with all stakeholders for consensus
- **Version Control**: Store plan versions to track changes over time
- **Regular Updates**: Keep the plan synchronized with actual implementation
