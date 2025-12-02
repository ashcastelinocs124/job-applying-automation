from tools import web_search_tool, serp_dev_tool,file_read_tool
from crewai import Crew, Agent, Task
from crewai_tools.tools import WebsiteSearchTool, SerperDevTool, FileReadTool

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

class Tasks:
  def research_company_culture_task(self, agent, company_description, company_domain):
        return Task(
            description=dedent(
                f"""\
								Analyze the provided company website and the hiring manager's company's domain {company_domain}, description: "{company_description}". Focus on understanding the company's culture, values, and mission. Identify unique selling points and specific projects or achievements highlighted on the site.
								Compile a report summarizing these insights, specifically how they can be leveraged in a job posting to attract the right candidates."""
            ),
            expected_output=dedent(
                """\
								A comprehensive report detailing the company's culture, values, and mission, along with specific selling points relevant to the job role. Suggestions on incorporating these insights into the job posting should be included."""
            ),
            agent=agent,
        )
  def research_role_requirements_task(self, agent, hiring_needs):
        return Task(
            description=dedent(
                f"""\
								Based on the hiring manager's needs: "{hiring_needs}", identify the key skills, experiences, and qualities the ideal candidate should possess for the role. Consider the company's current projects, its competitive landscape, and industry trends. Prepare a list of recommended job requirements and qualifications that align with the company's needs and values."""
            ),
            expected_output=dedent(
                """\
								A list of recommended skills, experiences, and qualities for the ideal candidate, aligned with the company's culture, ongoing projects, and the specific role's requirements."""
            ),
            agent=agent,
        )
  
  def research_company_background(self, agent, company_name):
     return Task(
        description = dedent(
           f"""\
           Analyze and summarize the company information {company_name}"""
        ),
        expected_output=dedent(
                """\
								A clear summary of what the company does."""
            ),
            agent=agent,
        )
  
  



