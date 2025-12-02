# 📚 Learning Resources

> **MODE: LEARNING** - This document is for understanding concepts, principles, and how things work. When you refer to this file, I'm in learning mode and will prioritize explanations and understanding over quick code solutions.

This document contains explanations and learning materials for the Job Application Assistant project.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Technologies](#technologies)
3. [Code Explanations](#code-explanations)
4. [Common Questions](#common-questions)

---

## Core Concepts

### Multi-Agent Systems
A multi-agent system uses multiple independent AI agents working together to solve complex tasks.

**In this project:**
- Each agent has a specific role (Researcher, Writer, Editor)
- Agents have access to different tools
- Tasks are distributed between agents based on expertise
- Agents can share information through the Crew orchestration

**Learn more:** [CrewAI Documentation](https://docs.crewai.com/)

### Prompting & Task Design
Tasks are instructions given to agents that guide their behavior.

**Components:**
- **Role**: What the agent is (e.g., "Research Analyst")
- **Goal**: What the agent aims to achieve
- **Tools**: What resources the agent can use
- **Backstory**: Context that shapes the agent's approach
- **Task Description**: Specific instructions for a task
- **Expected Output**: What the task should produce

### Tool Integration
Tools extend what agents can do. Common tools in this project:

| Tool | Purpose |
|------|---------|
| `WebsiteSearchTool` | Search and analyze websites |
| `SerperDevTool` | Search the internet for information |
| `FileReadTool` | Read and process files (resume, cover letter) |

---

## Technologies

### CrewAI Framework
**What it is:** A Python framework for orchestrating AI agents

**Key Classes:**
- `Agent` - Defines an AI agent with role, goal, tools, and backstory
- `Task` - Defines work for an agent to complete
- `Crew` - Orchestrates multiple agents working together

**Example pattern:**
```python
# Define an agent
agent = Agent(
    role="Research Analyst",
    goal="Find company insights",
    tools=[search_tool],
    backstory="Expert researcher",
    verbose=True
)

# Give it a task
task = Task(
    description="Research company culture",
    expected_output="Culture analysis report",
    agent=agent
)

# Execute with a crew
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

### Python textwrap.dedent()
**Purpose:** Removes common leading whitespace from multi-line strings

**Why use it:**
```python
# Bad - indentation shows up in the string
description = """
    This is indented
    In the code
"""  # Results in: "    This is indented\n    In the code\n"

# Good - dedent removes the common indentation
description = dedent("""
    This looks clean
    In the code
""")  # Results in: "This looks clean\nIn the code\n"
```

**Common pattern in tasks:**
```python
from textwrap import dedent

task = Task(
    description=dedent(f"""\
        Analyze {company} culture and values.
        Focus on: {focus_areas}
    """),
    expected_output=dedent("""\
        A comprehensive culture analysis
        Including key values and insights
    """),
    agent=agent
)
```

The `\` at the end of `"""` prevents a leading newline.

### OpenAI API
**What it is:** The language model powering your agents

**Required:**
- `OPENAI_API_KEY` environment variable
- Active OpenAI account with credits

**Models commonly used:**
- `gpt-4` - Most capable
- `gpt-3.5-turbo` - Faster, cheaper

### Environment Variables (.env)
**Purpose:** Store sensitive keys safely without committing to git

**Setup:**
```bash
# .env file
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
```

**Why important:**
- Never commit API keys to git
- Different values for dev/prod
- Easy to manage secrets

**Loading in code:**
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

---

## Code Explanations

### agents.py Structure

#### Agents Class
```python
class Agents:
    def research_agent(self):
        return Agent(...)  # Defines research agent
    
    def writer_agent(self):
        return Agent(...)  # Defines writing agent
    
    def review_agent(self):
        return Agent(...)  # Defines editing agent
```

**Pattern explanation:**
- Each method returns a new Agent instance
- Agents are defined once, instantiated when needed
- Allows reusability across different crews

#### Tasks Class
```python
class Tasks:
    def research_company_culture_task(self, agent, company_description, company_domain):
        return Task(
            description=dedent(f"""\
                Analyze company at {company_domain}...
            """),
            expected_output=dedent("""\
                A comprehensive culture report...
            """),
            agent=agent
        )
```

**Key concepts:**
- Tasks take an agent parameter - they're assigned to agents
- `f-strings` allow dynamic content (company names, domains)
- `dedent()` keeps code readable while producing clean output
- `expected_output` guides what the agent should produce

### tools.py Structure

```python
from crewai_tools import WebsiteSearchTool, SerperDevTool, FileReadTool

web_search_tool = WebsiteSearchTool()
serp_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path="job_description_example.md",
    description="A tool used to read the job description example"
)
```

**Explanation:**
- Tools are instantiated once at module level
- Can be passed to multiple agents
- `FileReadTool` requires specifying which file to read

---

## Common Questions

### Error Debugging Guide

When you encounter an error, I will:

1. **🔍 Identify the Root Cause** - Explain what went wrong and why
2. **📍 Locate the Issue** - Show the exact file, line number, and code context
3. **🔧 Suggest a Fix** - Provide concrete solutions with code examples
4. **📚 Link to Learning** - Reference relevant concepts from this document
5. **🛡️ Prevent Future Issues** - Explain how to avoid similar errors

**Common error types you might encounter:**

#### ValidationError (from Pydantic)
**What it means:** Your data doesn't match expected types or requirements
**Common causes:** Missing environment variables, invalid input types, missing required fields
**Example fix:** See "Why do I get 'OPENAI_API_KEY not set' error?" below

#### ImportError / ModuleNotFoundError
**What it means:** Python can't find a module you're trying to import
**Common causes:** Package not installed, wrong import path, typo in import statement
**Example fix:** Ensure all packages are installed: `pip install crewai crewai-tools`

#### AttributeError
**What it means:** You're trying to access an attribute that doesn't exist
**Common causes:** Typo in attribute name, object type mismatch, agent/task not properly initialized
**Example fix:** Check the correct attribute names in the API documentation

#### TypeError
**What it means:** Wrong type passed to a function or operation
**Common causes:** Passing string when int expected, None instead of object, wrong function arguments
**Example fix:** Verify parameter types match function signature

---

### Q: What's the difference between Agent and Task?
**A:** 
- **Agent** = WHO (a role with capabilities)
- **Task** = WHAT (specific work to do)
- An agent receives tasks to complete

### Q: Why use Crew?
**A:** Crews orchestrate multiple agents:
- Execute tasks in sequence or parallel
- Pass outputs between agents
- Handle failures and retries
- Provide logging and monitoring

### Q: How do agents access tools?
**A:** 
```python
Agent(
    role="Researcher",
    tools=[web_search_tool, serp_dev_tool],  # Available tools
    ...
)
```
Agents use available tools autonomously to complete tasks.

### Q: What happens when I call crew.kickoff()?
**A:**
1. Crew executes tasks in order (or parallel if configured)
2. Each task goes to its assigned agent
3. Agent uses tools and reasoning to complete it
4. Results are passed to next task/agent
5. Returns final output

### Q: Why do I get "OPENAI_API_KEY not set" error?
**A:** 
- Your `.env` file doesn't have the key set
- Or `.env` file is in wrong location (should be project root)
- Solution: Create `.env` with `OPENAI_API_KEY=sk-...`

### Q: Can multiple agents use the same tool?
**A:** Yes! Tools are shared resources:
```python
agent1 = Agent(tools=[web_search_tool, serp_dev_tool])
agent2 = Agent(tools=[web_search_tool, file_read_tool])
# Both can use web_search_tool
```

### Q: What's the difference between SerperDevTool and WebsiteSearchTool?
**A:**
- **SerperDevTool** = General internet search (like Google)
- **WebsiteSearchTool** = Search specific website content
- Use both: SerperDevTool finds companies, WebsiteSearchTool analyzes their sites

---

## Next Steps

1. **Read the code:** Review agents.py and tools.py with these concepts in mind
2. **Run a simple crew:** Execute a basic task to see agents in action
3. **Experiment:** Modify task descriptions and see how agents respond
4. **Extend:** Add new agents or tools as needed

## Resources

- [CrewAI Docs](https://docs.crewai.com/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [OpenAI Models](https://platform.openai.com/docs/models)
- [Python textwrap](https://docs.python.org/3/library/textwrap.html)

