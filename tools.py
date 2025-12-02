from crewai import Crew, Agent, Task
from crewai_tools import WebsiteSearchTool, SerperDevTool, FileReadTool
import agentops
import os
from dotenv import load_dotenv
from textwrap import dedent


load_dotenv(dotenv_path=".github/.env")


agentops.init(
    auto_start_session= False,trace_name= "CrewAI Job Posting", tags = ["crewai","job-posting","agentops-example"]
)
web_search_tool = WebsiteSearchTool()
serp_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path = "job_description_example.md",
    description = "A tool used to read the job description example"
)