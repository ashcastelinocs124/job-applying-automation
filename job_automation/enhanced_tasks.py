"""
Enhanced Tasks for Advanced Job Automation Features
"""

from crewai import Task
from textwrap import dedent


class EnhancedTasks:
    """Additional specialized tasks for advanced features"""
    
    def interview_preparation_task(self, agent, job_description, company_info):
        """Create comprehensive interview preparation materials"""
        return Task(
            description=dedent(f"""\
                Prepare comprehensive interview materials for the following role:
                
                Job Description: {job_description}
                Company Information: {company_info}
                
                Research and provide:
                1. Top 20 likely interview questions specific to this role
                2. STAR method response templates for behavioral questions
                3. Company-specific questions to prepare for
                4. Questions the candidate should ask the interviewer
                5. Common technical/skill assessments for this role type
                6. Interview format expectations (phone, video, panel, etc.)
                7. Company interview process and timeline insights
                8. Red flags to watch for during the interview
            """),
            expected_output=dedent("""\
                A comprehensive interview preparation guide including:
                - Categorized interview questions with sample answers
                - Behavioral response templates using STAR method
                - Company culture fit questions and answers
                - Strategic questions to ask interviewers
                - Technical assessment preparation tips
                - Interview logistics and format guidance
                - Success tips specific to the company's interview style
            """),
            agent=agent
        )
    
    def salary_research_task(self, agent, job_title, location, experience_level, company_name):
        """Research salary ranges and negotiation strategies"""
        return Task(
            description=dedent(f"""\
                Research comprehensive salary information for:
                
                Position: {job_title}
                Location: {location}
                Experience Level: {experience_level}
                Company: {company_name}
                
                Provide:
                1. Market salary range (25th, 50th, 75th percentile)
                2. Company-specific salary insights if available
                3. Total compensation breakdown (base, bonus, equity, benefits)
                4. Factors affecting salary at this company
                5. Negotiation strategies and tactics
                6. Common benefits to negotiate beyond base salary
                7. Regional cost of living adjustments
                8. Industry salary trends and projections
            """),
            expected_output=dedent("""\
                A detailed compensation analysis report including:
                - Specific salary ranges with data sources
                - Total compensation package breakdown
                - Company-specific compensation insights
                - Negotiation strategy playbook
                - Benefits negotiation guide
                - Market positioning analysis
                - Cost of living considerations
                - Timing and tactics for salary discussions
            """),
            agent=agent
        )
    
    def job_match_analysis_task(self, agent, resume, job_description):
        """Analyze job fit and provide matching score"""
        return Task(
            description=dedent(f"""\
                Perform detailed job match analysis:
                
                Resume: {resume}
                Job Description: {job_description}
                
                Analyze and provide:
                1. Overall match score (0-100%)
                2. Required skills match breakdown
                3. Preferred skills match breakdown
                4. Experience level alignment
                5. Educational requirements match
                6. Identified skill gaps with priority ranking
                7. Transferable skills that compensate for gaps
                8. Specific recommendations to improve match score
                9. Keywords missing from resume
                10. Strengths to highlight in application
            """),
            expected_output=dedent("""\
                A comprehensive job match analysis including:
                - Overall match score with detailed breakdown
                - Skills matrix (Required vs. Possessed)
                - Gap analysis with priority levels
                - Transferable skills assessment
                - Specific improvement recommendations
                - Keywords optimization suggestions
                - Application strategy based on match level
                - Quick wins to improve candidacy
            """),
            agent=agent
        )
    
    def linkedin_optimization_task(self, agent, current_profile, target_role, industry):
        """Optimize LinkedIn profile for visibility and engagement"""
        return Task(
            description=dedent(f"""\
                Optimize LinkedIn profile for maximum impact:
                
                Current Profile: {current_profile}
                Target Role: {target_role}
                Industry: {industry}
                
                Provide:
                1. Optimized headline (120 characters max)
                2. Compelling summary/about section
                3. Keyword strategy for {industry} and {target_role}
                4. Skills section optimization (top 10 skills to feature)
                5. Experience descriptions with achievement metrics
                6. Recommendations strategy
                7. Content strategy for thought leadership
                8. Network expansion tactics
                9. Profile completeness checklist
                10. LinkedIn SEO best practices
            """),
            expected_output=dedent("""\
                Complete LinkedIn optimization guide including:
                - New optimized headline options (3 versions)
                - Rewritten about/summary section
                - Strategic keyword placement guide
                - Top skills to feature and endorse
                - Experience section templates with metrics
                - Networking message templates
                - Content calendar suggestions
                - Profile optimization checklist
                - Action plan for profile improvement
            """),
            agent=agent
        )
    
    def email_templates_task(self, agent, scenario, target_role, company_info):
        """Create professional email templates for job search"""
        return Task(
            description=dedent(f"""\
                Create professional email templates for job search scenario:
                
                Scenario: {scenario}
                Target Role: {target_role}
                Company Info: {company_info}
                
                Create templates for:
                1. Cold outreach to hiring managers
                2. Follow-up after application submission
                3. Thank you note after interview
                4. Networking request to employees
                5. Informational interview request
                6. Referral request
                7. Rejection follow-up for future opportunities
                8. Salary negotiation email
                
                Each template should include:
                - Subject line options
                - Email body with customization placeholders
                - Call-to-action
                - Professional sign-off
            """),
            expected_output=dedent("""\
                Complete email template collection including:
                - 8+ email templates for different scenarios
                - Multiple subject line options per template
                - Customization guidelines
                - Timing recommendations
                - Follow-up sequences
                - Do's and don'ts for each template type
                - Success metrics to track
            """),
            agent=agent
        )
    
    def skills_gap_analysis_task(self, agent, current_skills, target_role_requirements):
        """Identify skill gaps and create learning plan"""
        return Task(
            description=dedent(f"""\
                Analyze skill gaps and create development plan:
                
                Current Skills: {current_skills}
                Target Role Requirements: {target_role_requirements}
                
                Provide:
                1. Detailed skill gap analysis
                2. Priority ranking of skills to develop
                3. Recommended online courses (free and paid)
                4. Relevant certifications with ROI analysis
                5. Books and resources for self-study
                6. Practical projects to demonstrate skills
                7. Timeline for skill development
                8. Budget considerations
                9. Quick wins vs. long-term investments
                10. Alternative paths if gaps are too large
            """),
            expected_output=dedent("""\
                Comprehensive skills development plan including:
                - Prioritized skill gap matrix
                - Specific course recommendations with links
                - Certification roadmap with costs and timeline
                - Resource library (books, websites, tools)
                - Project ideas to build portfolio
                - 30-60-90 day learning plan
                - Budget optimization strategies
                - Progress tracking framework
                - Alternative career paths if applicable
            """),
            agent=agent
        )
    
    def application_tracking_task(self, agent, applications_data):
        """Analyze application patterns and provide insights"""
        return Task(
            description=dedent(f"""\
                Analyze job application data and provide insights:
                
                Applications Data: {applications_data}
                
                Analyze and provide:
                1. Response rate analysis
                2. Best performing resume versions
                3. Most successful application channels
                4. Optimal application timing patterns
                5. Company response time averages
                6. Interview conversion rates
                7. Common rejection reasons
                8. Improvement recommendations
                9. A/B testing suggestions
                10. Follow-up strategy effectiveness
            """),
            expected_output=dedent("""\
                Application analytics report including:
                - Success metrics dashboard
                - Performance trends and patterns
                - Channel effectiveness analysis
                - Timing optimization insights
                - Resume version performance
                - Actionable improvement recommendations
                - A/B testing framework
                - Follow-up strategy refinements
                - Predictive success factors
            """),
            agent=agent
        )