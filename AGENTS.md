# Repository Guidelines

## Project Structure & Module Organization
- `job_automation/` hosts the CrewAI-powered workflow: `agents.py`, `tasks.py`, `tools.py`, and `utils.py` define the core orchestration, `sample.py` supplies demo data, `main.py` runs the crew pipeline, and `app.py` exposes the Streamlit UI. Keep an eye on `job_automation/AGENTS.md` and `instructions.md` for deeper agent- and workflow-level guidance.
- Other folders (e.g., `coding-terminal/`, `coffee-machine/`, `educational_module_creator/`, `documentation-mcp/`) are self-contained experiments. Treat each as its own module, add README/AGENTS if you extend them, and do not assume shared configuration unless noted.
- Root assets such as `readme.md` describe the Job Automation project, while artifacts like `.pdf`/`.log` files (e.g., `resume.pdf`, `agentops.log`) are outputs—do not edit them directly.

## Build, Test, and Development Commands
- Install the minimum dependencies for the automation tool: `pip install crewai fpdf python-dotenv`.
- Launch the scripted pipeline with `python job_automation/main.py` to regenerate resumes/cover letters from the sample data.
- Start the UI with `streamlit run job_automation/app.py` to exercise the tabbed workflow interactively.
- (Future) Run automated suites with `python -m pytest` once tests exist; point pytest at `tests/` subfolders and include `tests/test_*.py` files for coverage.
- Check for `.env` keys before running any command; missing keys are surfaced in the UI and scripts via the helper in `tools.py`.

## Coding Style & Naming Conventions
- Use four-space indentation and follow the standard Python import order: standard library ⇒ third-party ⇒ local modules, with `sys.path` manipulations near the top of entry scripts.
- Prefer descriptive variables (`cover_letter_agent`, `company_description`) plus verb-based function names (`run_cover_letter_generation`) and PascalCase classes (`Agents`, `Tasks`, `PDFResume`).
- Keep CrewAI definitions readable: wrap multi-line task descriptions in `dedent()`, list only initialized tools, and annotate functions/returns with type hints where practical.

## Testing Guidelines
- The project currently lacks automated tests; consider adding `pytest` or similar under a `tests/` directory and include `test_agents.py`, `test_tools.py`, etc.
- Name files and fixtures `tests/test_<feature>.py` so automation tools (and contributors) know what to run.
- When you add a test, document how to invoke it (e.g., `python -m pytest tests/test_agents.py -v`) either in a README or this guide.

## Commit & Pull Request Guidelines
- Follow Conventional Commits seen in history (`feat(...):`, `fix(...):`, etc.) so changelog generation stays consistent.
- Each PR should describe the change, link to any issue or task, and note any manual verification steps (UI screenshots for Streamlit changes are helpful).
- Update this AGENTS file or the relevant subproject doc when you alter workflows, tools, or onboarding steps.

## Security & Configuration Tips
- Never commit actual API keys—store them in `.env` files and verify that `OPENAI_API_KEY` / `SERPER_DEV_API_KEY` are set before running agents.
- When adding new dependencies, document them in the relevant subproject folder (e.g., `requirements.txt` inside `documentation-mcp/`) and replicate the install command in this guide if it affects the shared workflow.
