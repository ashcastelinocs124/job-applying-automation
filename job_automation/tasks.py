from job_automation.tools import web_search_tool, serp_dev_tool,file_read_tool
from crewai import Crew, Agent, Task


from dotenv import load_dotenv
from textwrap import dedent



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
           Analyze aßnd summarize the company information {company_name}"""
        ),
        expected_output=dedent(
                """\
								A clear summary of what the company does."""
            ),
            agent=agent,
        )
  
  def generate_cover_letter_task(self, agent, resume_content, job_posting, company_culture_insights):
    return Task(
        description=dedent(
            f"""\
            Write a compelling cover letter based on the following:
            
            Resume Content: {resume_content}
            
            Job Posting: {job_posting}
            
            Company Culture & Values: {company_culture_insights}
            
            The cover letter should:
            - Open with a strong hook that shows genuine interest in the company
            - Highlight 2-3 key skills from the resume that match the job requirements
            - Demonstrate understanding of the company's culture and values
            - Include specific examples of relevant achievements
            - Close with a clear call to action
            - Maintain a professional yet personable tone
            - Be 3-4 paragraphs long"""
        ),
        expected_output=dedent(
            """\
            A polished, personalized cover letter (3-4 paragraphs) that:
            - Opens with genuine interest in the role and company
            - Demonstrates alignment between candidate skills and job requirements
            - Shows understanding of company culture
            - Includes specific, relevant examples
            - Has a strong closing with call to action
            - Is error-free and professionally formatted"""
        ),
        agent=agent,
    )
  def generate_resume_task(self, agent, resume_content, job_posting, company_culture_insights):
    return Task(
      description=dedent(
        f"""\
        Write a Resume based on the following:

        Resume Content: {resume_content}
        Job Posting: {job_posting}
        Company Culture & Values: {company_culture_insights}

        The Resume should:
        - Highlight the skills that are relevant to the job posting
        - Use a professional format suitable for the industry
        - Be clear, concise, and free of grammatical errors
        - Emphasize achievements and quantifiable results
        - Tailor the summary and experience sections to the specific role
        """
      ),
      expected_output=dedent(
        """\
        A professional, tailored resume that:
        - Accurately reflects the candidate's skills and experience
        - Is optimized for the specific job posting
        - Aligns with the company's culture and values
        - Uses strong action verbs and quantifiable metrics
        - Is formatted for readability and ATS compatibility
        """
      ),
      agent=agent
    )
  