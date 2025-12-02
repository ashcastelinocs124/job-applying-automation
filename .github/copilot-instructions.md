# Co-Pilot Instructions

## Project Context

This is a **Job Application Assistant** personal project that uses AI agents to automate and enhance job application workflows.

### Project Goal
Build an intelligent system that takes a user's resume and cover letter, then uses CrewAI agents to:
- Research company culture and values from their website
- Analyze role requirements and job descriptions
- Generate tailored job postings or application materials
- Review and edit content for clarity and engagement

### Tech Stack
- **Framework**: CrewAI (Multi-agent orchestration)
- **Tools**: CrewAI Tools (WebsiteSearchTool, SerperDevTool, FileReadTool)
- **Monitoring**: AgentOps
- **Language Model**: OpenAI API
- **Environment**: Python 3.11+

### Project Structure
```
Personal_Projects/
├── tools.py          # Tool definitions (WebsiteSearchTool, SerperDevTool, FileReadTool)
├── agents.py         # Agent and Task definitions
├── .env              # API keys and environment variables
└── .github/
    ├── co-pilot.instructions.md  # This file
    └── learning.md               # Learning resources and explanations
```

### Key Agents
1. **Research Analyst** - Analyzes company websites and descriptions
2. **Writer** - Crafts engaging content based on research
3. **Review & Editing Specialist** - Reviews content for clarity and correctness

---

## Interaction Modes

### 📚 Learning Mode (Default for Questions)
When asking questions (starting with "what", "how", "explain", "why"), Co-Pilot will:
- Refer to **[learning.md](./learning.md)** for detailed explanations
- Teach concepts and underlying principles
- Provide step-by-step understanding
- Include examples and use cases
- Help you learn the technology stack (CrewAI, Pydantic, async patterns, etc.)

**Example**: "What is dedent?" → Refers to learning.md, explains the concept

### 💻 Implementation Mode
When implementing features or fixing bugs:
- Provide working code solutions
- Explain implementation choices
- Link to relevant learning resources

### 🐛 Debug Mode
When troubleshooting errors:
- Identify root cause
- Suggest fixes with explanations
- Point to learning resources for deeper understanding

---

## Important Links
- **Learning Resources**: See [learning.md](./learning.md)
- **CrewAI Docs**: https://docs.crewai.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **OpenAI API**: https://platform.openai.com/docs/

---

## Development Guidelines

### Before Asking Questions
Consider checking:
1. [learning.md](./learning.md) - For concept explanations
2. Code comments in agents.py and tools.py
3. Official documentation links above

### Code Standards
- Use type hints
- Follow PEP 8
- Add docstrings to functions
- Use dedent for multi-line strings in tasks

### Environment Setup
Ensure `.env` contains:
```
OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-key-here
```

---

## Current Status
- ✅ Project structure initialized
- ✅ Dependencies installed (Python 3.11)
- ✅ Agents and Tasks framework set up
- 🔄 Integration and testing in progress

