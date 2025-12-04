import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agentops
from job_automation.agents import Tasks, Agents
from crewai import Crew, Agent, Task
from job_automation.sample import sample_resume, sample_job_posting, sample_company_culture


tracer = agentops.start_trace(trace_name="CrewAI Job Posting", tags=["crew-job-posting-example", "agentops-example"])
tasks = Tasks()
agents = Agents()
company_description = "We are a software company that builds AI-powered tools for businesses."
company_domain = "https://www.agentops.ai"
hiring_needs = "We are looking for a software engineer with 3 years of experience in Python and Django."
specific_benefits = "We offer a competitive salary, health insurance, and a 401k plan."
company_name = "agentops"


researcher_agent = agents.research_agent()
writer_agent = agents.writer_agent()
review_agent = agents.review_agent()
cover_letter_agent = agents.cover_letter_agent()

research_company_culture_task = tasks.research_company_culture_task(
    researcher_agent, company_description, company_domain
)
research_role_requirements_task = tasks.research_role_requirements_task(researcher_agent, hiring_needs)
review_and_edit_job_posting_task = tasks.research_company_background(researcher_agent, company_name)
generate_cover_letter = tasks.generate_cover_letter_task(cover_letter_agent,sample_resume,sample_job_posting,sample_company_culture)


# Instantiate the crew with a sequential process
crew = Crew(
    agents=[researcher_agent, writer_agent, review_agent, cover_letter_agent],
    tasks=[
        research_company_culture_task,
        research_role_requirements_task,
        review_and_edit_job_posting_task,
        generate_cover_letter
    ],
)

result = crew.kickoff()

print(result)