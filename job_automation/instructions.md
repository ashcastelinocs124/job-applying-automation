# Job Automation - Project Instructions

## Overview
This is an AI-powered job application automation tool that uses CrewAI multi-agent workflows to generate personalized cover letters, tailor resumes, and research companies. The project combines sophisticated AI agent orchestration with a user-friendly Streamlit web interface.

## Architecture

### Core Components
- **Agents** (`agents.py`): 5 specialized AI agents (Research, Writer, Review, Cover Letter, Resume)
- **Tasks** (`tasks.py`): Detailed task definitions with specific instructions and expected outputs
- **Tools** (`tools.py`): External tool integration (web search, file reading) with error handling
- **Utils** (`utils.py`): PDF generation utilities for professional resume output
- **Web Interface** (`app.py`): Streamlit-based interactive UI with tabbed workflows
- **Sample Data** (`sample.py`): Test data for development and demonstration

### Entry Points
- **Script**: `python main.py` - Direct execution of CrewAI workflows with file output
- **Web App**: `streamlit run app.py` - Interactive interface with multiple tabs

## Development Setup

### Environment Requirements
```bash
# Install dependencies
pip install -r requirements.txt

# Required environment variables in .env file:
OPENAI_API_KEY=your_openai_key
SERPER_DEV_API_KEY=your_serper_key
```

### Key Dependencies
- **CrewAI** (>=0.28.0): Multi-agent orchestration framework
- **Streamlit** (>=1.30.0): Web interface framework
- **OpenAI** (>=1.3.0): LLM integration
- **AgentOps** (>=0.1.0): AI agent monitoring and tracing
- **python-docx** (>=0.8.11): DOC file generation
- **fpdf**: PDF generation (included in utils.py)

## Code Conventions

### Import Structure
```python
# Standard library imports first
import sys
import os

# Path manipulation for module resolution (current directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Third-party imports
import streamlit as st
from crewai import Crew, Agent, Task
from docx import Document

# Local imports (relative to current directory)
from agents import Agents
from tasks import Tasks
from utils import parse_markdown_to_pdf
```

### Naming Conventions
- **Classes**: PascalCase (`Agents`, `Tasks`, `PDFResume`)
- **Functions**: verb phrases (`run_cover_letter_generation()`, `research_company_culture_task()`)
- **Variables**: descriptive names (`cover_letter_agent`, `company_description`)
- **Files**: lowercase with underscores (`agents.py`, `tools.py`)

### CrewAI Patterns
```python
# Agent definition
def research_agent(self):
    return Agent(
        role="Research Analyst",
        goal="Analyze company website and description for culture insights",
        tools=[tool for tool in [get_web_search_tool(), get_serp_dev_tool()] if tool is not None],
        backstory="Expert in analyzing company cultures and identifying key values",
        verbose=True,
    )

# Task definition
def research_company_culture_task(self, agent, company_description, company_domain):
    return Task(
        description=dedent(f"""\
            Analyze the provided company website {company_domain} and description: 
            "{company_description}". Focus on understanding culture, values, and mission.
            Compile a report with insights for job posting optimization."""),
        expected_output=dedent("""\
            A comprehensive report detailing company culture, values, and mission,
            along with specific selling points relevant to the job role."""),
        agent=agent,
    )
```

## Workflows

### 1. Company Research Workflow
- **Input**: Company description, website domain, hiring needs
- **Process**: Research agent analyzes company culture and role requirements
- **Output**: Comprehensive company insights report

### 2. Cover Letter Generation
- **Input**: Resume content, job posting, company culture insights
- **Process**: Cover letter agent creates personalized, compelling letter
- **Output**: Professional cover letter (3-4 paragraphs) in DOC format

### 3. Resume Tailoring
- **Input**: Current resume, job description, company background
- **Process**: Resume agent optimizes content for specific role
- **Output**: Tailored resume in PDF format with markdown parsing

### 4. Full Pipeline (main.py)
- **Input**: Resume, job posting, company info
- **Process**: Sequential execution of research → cover letter → resume
- **Output**: Complete application package (PDF resume + DOC cover letter)

## File Output Generation

### PDF Resume Generation
```python
from utils import parse_markdown_to_pdf
parse_markdown_to_pdf(resume_content, "tailored_resume.pdf")
```

### DOC Cover Letter Generation
```python
from docx import Document
doc = Document()
doc.add_heading('Cover Letter', 0)
doc.add_paragraph(cover_letter_content)
doc.save("cover_letter.docx")
```

### Error Handling for File Generation
- Always wrap file generation in try/except blocks
- Provide fallback to text files if PDF/DOC generation fails
- Give clear feedback to users about generated files

## Error Handling Guidelines

### Tool Initialization
```python
def get_web_search_tool():
    try:
        return WebsiteSearchTool()
    except Exception as e:
        print(f"Warning: Could not initialize WebsiteSearchTool: {e}")
        return None
```

### API Key Validation
```python
def check_api_keys():
    missing_keys = []
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    if not os.getenv("SERPER_DEV_API_KEY"):
        missing_keys.append("SERPER_DEV_API_KEY")
    return missing_keys
```

### User-Facing Errors
- Provide clear, actionable error messages in Streamlit UI
- Validate inputs before processing
- Graceful degradation when tools are unavailable
- Show progress indicators for long-running operations

## Testing and Development

### Current State
- **No test framework configured** - consider adding pytest
- Uses `sample.py` for demonstration data
- Manual testing through Streamlit interface
- File output testing with sample data

### Recommended Testing Approach
```bash
# Add testing dependencies
pip install pytest pytest-asyncio

# Create test structure
tests/
├── test_agents.py
├── test_tasks.py
├── test_tools.py
├── test_utils.py
└── test_workflows.py
```

## Deployment Considerations

### Environment Variables
- Never commit API keys to repository
- Use `.env` files for local development
- Configure secure environment variable management for production

### Performance
- AgentOps integration provides monitoring and tracing
- Consider rate limiting for API calls
- Implement caching for repeated company research
- Optimize file generation for large documents

## Common Development Tasks

### Adding a New Agent
1. Define agent in `agents.py` with role, goal, backstory, tools
2. Create corresponding tasks in `tasks.py`
3. Update workflows in `main.py` and `app.py`
4. Add UI components if needed
5. Test file output generation

### Modifying Workflows
1. Update task definitions in `tasks.py`
2. Modify crew composition in workflow functions
3. Update Streamlit UI tabs and input handling
4. Test with sample data
5. Verify file output formats

### Adding New Tools
1. Implement tool initialization in `tools.py` with error handling
2. Add to agent tool lists as needed
3. Update environment variable requirements
4. Document usage in agent backstories

### File Output Integration
1. Use `parse_markdown_to_pdf()` for PDF generation
2. Use `python-docx` Document class for DOC files
3. Always provide fallback text file options
4. Include proper error handling and user feedback

## Best Practices

1. **Always validate environment variables** before agent initialization
2. **Use descriptive task descriptions** with clear expected outputs
3. **Handle tool failures gracefully** with None returns and warnings
4. **Provide user feedback** in Streamlit UI for long-running operations
5. **Use AgentOps tracing** for monitoring and debugging
6. **Follow the established import pattern** with relative imports
7. **Keep agent roles focused** and well-defined
8. **Test with sample data** before using real user input
9. **Generate professional file outputs** with proper error handling
10. **Document file formats** and provide clear user instructions