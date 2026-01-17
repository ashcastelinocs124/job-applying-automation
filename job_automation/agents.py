from tools import (
    get_web_search_tool,
    get_serp_dev_tool,
    get_file_read_tool,
)
from crewai import Crew, Agent, Task
from crewai_tools.tools import WebsiteSearchTool, SerperDevTool, FileReadTool

from dotenv import load_dotenv
from textwrap import dedent


class Agents:
    def research_agent(self):
        return Agent(
            role="Research Analyst",
            goal="Analyze the company website and provided description to extract insights on culture, values and specific needs",
            tools=[
                tool
                for tool in [get_web_search_tool(), get_serp_dev_tool()]
                if tool is not None
            ],
            backstory="Expert in analyzing company cultures and indentifying key values and needs",
            verbose=True,
        )

    def writer_agent(self):
        return Agent(
            role="Writer",
            goal="Craft engaging content based on provided information",
            backstory="Skilled in writing clear and compelling content for various purposes",
            verbose=True,
        )

    def review_agent(self):
        return Agent(
            role="Review and Editing Specialist",
            goal="Review the job posting for clarity, engagement, grammatical error",
            tools=[
                tool
                for tool in [
                    get_web_search_tool(),
                    get_serp_dev_tool(),
                    get_file_read_tool(),
                ]
                if tool is not None
            ],
            backstory="A detailed oriented editor with an eye for detail and every piece of content",
            verbose=True,
        )

    def cover_letter_agent(self):
        return Agent(
            role="Cover Letter specialist,",
            goal="Write personalized, compelling cover letter and align with company values",
            backstory="Expert at crafting persuasive cover letters that connect candidate strengths with job requirements and company culture",
            verbose=True,
        )

    def resume_agent(self):
        return Agent(
            role="Resume Specialist",
            goal="Write a personalized resume for job application",
            backstory="Expert at crafting great industry standard professional resume",
            verbose=True,
        )
