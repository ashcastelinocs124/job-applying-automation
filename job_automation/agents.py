from job_automation.tools import web_search_tool, serp_dev_tool,file_read_tool
from crewai import Crew, Agent, Task


from dotenv import load_dotenv
from textwrap import dedent

class Agents:

  def research_agent(self):
    return Agent(
        role = "Research Analyst",
        goal = "Analyze the company website and provided description to extract insights on culture, values and specific needs",
        tools = [web_search_tool, serp_dev_tool],
        backstory = "Expert in analyzing company cultures and indentifying key values and needs",
        verbose = True
    )

  def writer_agent(self):
    return Agent(
        role = "Writer",
        goal = "Craft engaging content based on provided information",
        backstory = "Skilled in writing clear and compelling content for various purposes",
        verbose = True
    )

  def review_agent(self):
    return Agent(
        role = "Review and Editing Specialist",
        goal = "Review the job posting for clarity, engagement, grammatical error",
        tools = [web_search_tool, serp_dev_tool, file_read_tool],
        backstory = "A detailed oriented editor with an eye for detail and every piece of content",
        verbose = True
    )
  def cover_letter_agent(self):
     return Agent(
        role = "Cover Letter speciliast,",
        goal = "Write personalized, compelling cover letter and align with company values",
        backstory = "Expert at crafting persuasive cover letters that connect candidate strenghts with job requirements and company culture",
        verbose = True
     )
  def resume_agent(self):
    return Agent(
      role = "Resume Writer Speciliast",
      goal = "Create a resume based on the user_background and job/company information",
      backstory = "Resume Expert that focuses on making a resume that connects the user background and job description",
      verbose = True
    )
    

