# Job Applying Automation

A Python-based automation tool for generating professional job application materials using multi-agent workflows.

## Overview

This project streamlines the process of applying for jobs by automating the generation of tailored resumes and compelling cover letters. Designed with modular agents and task orchestration (powered by [CrewAI](https://github.com/joaomdmoura/crewAI)), it analyzes company culture, job descriptions, and candidate profiles, producing customized application documents optimized for each opportunity.

## Features

- **Multi-Agent Workflow:**  
  Specialized agents handle research, writing, reviewing, and document generation (resume & cover letter).

- **Company Insight Extraction:**  
  Automatically analyzes company websites and descriptions to highlight values, culture, and differentiators.

- **Custom Content Generation:**  
  Produces cover letters and resumes aligned with job postings and company culture.

- **Professional Formatting:**  
  Outputs can be converted from markdown to PDF for easy submission.

- **Sample Data Included:**  
  Example resumes, job descriptions, and company culture profiles to demonstrate functionality.

## How it Works

1. **Agents Initialization:**  
   - `Research Agent`: Analyzes company and role requirements.
   - `Writer Agent`: Crafts engaging content.
   - `Review Agent`: Edits for clarity and professionalism.
   - `Cover Letter Agent` & `Resume Agent`: Generates respective documents.

2. **Task Pipeline:**  
   - Research company culture and role requirements.
   - Summarize company background.
   - Generate cover letter and resume based on insights and job posting.

3. **Output:**  
   - Applications are formatted and exported as PDFs using `parse_markdown_to_pdf`.

## Directory Structure

```
job_automation/
  ├── agents.py       # Agent definitions and roles
  ├── tasks.py        # Task definitions for agents
  ├── sample.py       # Sample resume, job descriptions, and company culture
  ├── tools.py        # External tools (web search, file read)
  ├── utils.py        # Markdown to PDF conversion
  ├── main.py         # Entry point
  └── __init__.py     # Module init
```

## Example Usage

Run the main automation script:

```bash
python job_automation/main.py
```

This will generate a tailored resume and cover letter PDF for the sample job description at AgentOps.

## Requirements

- Python 3.8+
- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [FPDF](https://pypi.org/project/fpdf/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install dependencies:

```bash
pip install crewai fpdf python-dotenv
```

## Customization

- Replace sample data in `sample.py` for your own resume, job posting, and company culture analysis.
- Integrate with other job boards or automation frameworks for broader job search support.

## Contributing

Pull requests are welcome! For major changes or suggestions, please open an issue first.

## License

MIT

---

**Maintainer:** [ashcastelinocs124](https://github.com/ashcastelinocs124)
