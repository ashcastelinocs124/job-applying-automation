"""
Enhanced Agents for Advanced Job Automation Features
"""

from crewai import Agent
from tools import get_web_search_tool, get_serp_dev_tool, get_file_read_tool
from textwrap import dedent


class EnhancedAgents:
    """Additional specialized agents for advanced features"""
    
    def interview_prep_agent(self):
        """Agent specialized in interview preparation"""
        return Agent(
            role="Interview Preparation Specialist",
            goal="Prepare comprehensive interview materials including common questions, behavioral responses, and company-specific insights",
            tools=[tool for tool in [get_web_search_tool(), get_serp_dev_tool()] if tool is not None],
            backstory=dedent("""\
                You are an experienced career coach with expertise in interview preparation.
                You have helped hundreds of candidates prepare for interviews at top companies.
                You understand different interview formats (behavioral, technical, case studies)
                and can provide tailored preparation materials based on the role and company.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def salary_research_agent(self):
        """Agent specialized in salary research and negotiation"""
        return Agent(
            role="Compensation Research Analyst",
            goal="Research market salary ranges and provide negotiation strategies",
            tools=[tool for tool in [get_serp_dev_tool()] if tool is not None],
            backstory=dedent("""\
                You are a compensation analyst with deep knowledge of salary trends,
                market rates, and negotiation tactics. You understand factors like
                location, experience, company size, and industry that affect compensation.
                You provide data-driven insights for salary negotiations.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def job_match_analyst(self):
        """Agent that analyzes job fit and provides matching scores"""
        return Agent(
            role="Job Match Analyst",
            goal="Analyze candidate profile against job requirements and provide detailed matching analysis",
            tools=[tool for tool in [get_file_read_tool()] if tool is not None],
            backstory=dedent("""\
                You are an expert in talent matching with years of experience in recruitment.
                You can identify skill gaps, transferable skills, and provide actionable
                recommendations for improving candidacy. You provide objective scoring
                based on requirement matches.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def linkedin_optimizer(self):
        """Agent specialized in LinkedIn profile optimization"""
        return Agent(
            role="LinkedIn Profile Optimization Expert",
            goal="Optimize LinkedIn profiles for better visibility and engagement",
            tools=[tool for tool in [get_web_search_tool()] if tool is not None],
            backstory=dedent("""\
                You are a LinkedIn expert who understands the platform's algorithm,
                SEO best practices, and how to create compelling professional narratives.
                You help professionals stand out with optimized headlines, summaries,
                and keyword strategies.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def email_template_agent(self):
        """Agent that creates professional email templates"""
        return Agent(
            role="Professional Communication Specialist",
            goal="Create compelling email templates for various job search scenarios",
            backstory=dedent("""\
                You are a business communication expert who crafts persuasive,
                professional emails. You understand email etiquette, how to grab
                attention, and how to communicate value concisely. You create
                templates for cold outreach, follow-ups, thank you notes, and
                networking messages.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def skills_gap_analyst(self):
        """Agent that identifies skill gaps and suggests learning paths"""
        return Agent(
            role="Skills Development Advisor",
            goal="Identify skill gaps and recommend learning resources and certifications",
            tools=[tool for tool in [get_serp_dev_tool(), get_web_search_tool()] if tool is not None],
            backstory=dedent("""\
                You are a career development specialist who helps professionals
                identify skill gaps and create learning plans. You know about
                various online courses, certifications, and resources that can
                help candidates become more competitive for their target roles.
            """),
            verbose=True,
            allow_delegation=False
        )