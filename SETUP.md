# Job Automation Tool - Setup Guide

## Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
SERPER_DEV_API_KEY=your_serper_api_key_here
AGENTOPS_API_KEY=your_agentops_api_key_here
```

## Required API Keys

### OpenAI API Key
- Get from: https://platform.openai.com/api-keys
- Required for: LLM operations, agent responses

### Serper Dev API Key  
- Get from: https://serper.dev/
- Required for: Web search functionality
- Free tier available

### AgentOps API Key (Optional)
- Get from: https://app.agentops.ai/
- Required for: Agent monitoring and tracing

## Installation

```bash
pip install -r job_automation/requirements.txt
```

## Running the Application

### Streamlit Web App
```bash
streamlit run job_automation/app.py
```

### Command Line Interface
```bash
python job_automation/main.py
```

## Features

- **Cover Letter Generation**: AI-powered personalized cover letters
- **Resume Building**: Tailored resumes for specific jobs
- **Company Research**: Automated company culture and insights
- **Full Pipeline**: Complete application workflow

## Troubleshooting

1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Errors**: Check your `.env` file has correct keys
3. **Tool Errors**: Some tools require valid API keys to function