# Job Automation - Agent Guidelines

## Build/Test Commands
- **Run app**: `streamlit run app.py`
- **Run main script**: `python main.py`
- **Install dependencies**: `pip install -r requirements.txt`
- **Test single file**: `python -m pytest tests/test_agents.py -v` (when pytest added)
- **Lint**: No linter configured - consider adding ruff or black
- **Type check**: No type checker configured - consider adding mypy

## Code Style Guidelines

### Imports & Structure
- Use relative imports: `from agents import Agents` (current working directory)
- Standard library imports first, then third-party, then local imports
- Use `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` for module resolution

### Formatting & Types
- Use descriptive variable names (e.g., `cover_letter_agent`, `company_description`)
- Function names: verb phrases (`run_cover_letter_generation()`, `research_company_culture_task()`)
- Class names: PascalCase (`Agents`, `Tasks`, `PDFResume`)
- Use type hints for function parameters and return values

### Error Handling
- Use try/except blocks for tool initialization with None returns
- Check for missing API keys before agent initialization
- Provide clear error messages in Streamlit UI with fallback options

### CrewAI Patterns
- Agents: Define role, goal, backstory, tools, verbose=True
- Tasks: Use dedent() for multi-line descriptions and expected_output
- Tools: Handle None returns gracefully when env vars missing
- Use Crew class with sequential process for multi-agent workflows

### File Generation
- PDF resumes: Use `parse_markdown_to_pdf()` from utils.py
- DOC cover letters: Use `python-docx` Document class
- Always provide fallback to text files if generation fails