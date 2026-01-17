"""
Job Automation Tool - Interactive Web Frontend
Built with Streamlit for a clean, interactive UI
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from crewai import Crew
from job_automation.agents import Agents
from job_automation.tasks import Tasks
from job_automation.sample import (
    sample_resume,
    sample_job_posting,
    sample_company_culture,
)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env")

# Page configuration
st.set_page_config(
    page_title="Job Application Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .output-box {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }
    .success-box {
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 15px;
        border-radius: 5px;
    }
    .info-box {
        background-color: #DBEAFE;
        border-left: 4px solid #3B82F6;
        padding: 15px;
        border-radius: 5px;
    }
</style>
""",
    unsafe_allow_html=True,
)


def check_api_keys():
    """Check if required API keys are present"""
    missing_keys = []

    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    if not os.getenv("SERPER_DEV_API_KEY"):
        missing_keys.append("SERPER_DEV_API_KEY")

    return missing_keys


def init_agents():
    """Initialize all agents and tasks"""
    missing_keys = check_api_keys()
    if missing_keys:
        raise Exception(
            f"Missing required API keys: {', '.join(missing_keys)}. Please set them in your .env file."
        )
    return Agents(), Tasks()


def run_cover_letter_generation(
    resume: str, job_posting: str, company_culture: str, progress_callback=None
):
    """Run the cover letter generation crew"""
    agents_instance, tasks_instance = init_agents()

    cover_letter_agent = agents_instance.cover_letter_agent()

    cover_letter_task = tasks_instance.generate_cover_letter_task(
        cover_letter_agent, resume, job_posting, company_culture
    )

    crew = Crew(agents=[cover_letter_agent], tasks=[cover_letter_task], verbose=True)

    result = crew.kickoff()
    return str(result)


def run_resume_generation(
    old_resume: str,
    job_description: str,
    company_background: str,
    progress_callback=None,
):
    """Run the resume generation crew"""
    agents_instance, tasks_instance = init_agents()

    resume_agent = agents_instance.resume_agent()

    resume_task = tasks_instance.generate_resume(
        resume_agent, old_resume, job_description, company_background
    )

    crew = Crew(agents=[resume_agent], tasks=[resume_task], verbose=True)

    result = crew.kickoff()
    return str(result)


def run_company_research(
    company_description: str,
    company_domain: str,
    hiring_needs: str,
    progress_callback=None,
):
    """Run the company research crew"""
    agents_instance, tasks_instance = init_agents()

    researcher_agent = agents_instance.research_agent()

    culture_task = tasks_instance.research_company_culture_task(
        researcher_agent, company_description, company_domain
    )

    requirements_task = tasks_instance.research_role_requirements_task(
        researcher_agent, hiring_needs
    )

    crew = Crew(
        agents=[researcher_agent], tasks=[culture_task, requirements_task], verbose=True
    )

    result = crew.kickoff()
    return str(result)


def run_full_pipeline(
    resume: str, job_posting: str, company_domain: str, company_description: str
):
    """Run the full job application pipeline"""
    agents_instance, tasks_instance = init_agents()

    # Initialize agents
    researcher_agent = agents_instance.research_agent()
    cover_letter_agent = agents_instance.cover_letter_agent()
    resume_agent = agents_instance.resume_agent()

    # Create tasks
    culture_task = tasks_instance.research_company_culture_task(
        researcher_agent, company_description, company_domain
    )

    cover_letter_task = tasks_instance.generate_cover_letter_task(
        cover_letter_agent,
        resume,
        job_posting,
        "Company culture insights will be gathered from research",
    )

    resume_task = tasks_instance.generate_resume(
        resume_agent, resume, job_posting, company_description
    )

    crew = Crew(
        agents=[researcher_agent, cover_letter_agent, resume_agent],
        tasks=[culture_task, cover_letter_task, resume_task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


# ==================== MAIN APP ====================


def main():
    # Header
    st.markdown(
        '<p class="main-header">🚀 Job Application Assistant</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">AI-powered tools to help you land your dream job</p>',
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/resume.png", width=80)
        st.markdown("### 📋 Quick Actions")

        use_sample_data = st.checkbox(
            "Use sample data",
            value=True,
            help="Load sample resume, job posting, and company info",
        )

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This tool uses AI agents to:
        - 🔍 Research companies
        - ✍️ Generate cover letters
        - 📄 Tailor your resume
        - 📝 Create job postings
        """)

        st.markdown("---")
        st.markdown("### 🔧 Settings")
        verbose_mode = st.checkbox("Verbose output", value=False)

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📝 Cover Letter",
            "📄 Resume Builder",
            "🔍 Company Research",
            "🚀 Full Pipeline",
        ]
    )

    # ==================== TAB 1: COVER LETTER ====================
    with tab1:
        st.markdown("### Generate a Tailored Cover Letter")
        st.markdown(
            "Provide your resume, the job posting, and company info to generate a personalized cover letter."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📋 Your Resume")
            resume_input = st.text_area(
                "Paste your resume here",
                value=sample_resume if use_sample_data else "",
                height=300,
                key="cl_resume",
            )

            st.markdown("#### 🏢 Company Culture")
            culture_input = st.text_area(
                "Company culture & values (or leave empty for research)",
                value=sample_company_culture if use_sample_data else "",
                height=200,
                key="cl_culture",
            )

        with col2:
            st.markdown("#### 💼 Job Posting")
            job_posting_input = st.text_area(
                "Paste the job description here",
                value=sample_job_posting if use_sample_data else "",
                height=520,
                key="cl_job",
            )

        if st.button(
            "✨ Generate Cover Letter",
            key="gen_cl",
            type="primary",
            use_container_width=True,
        ):
            if not resume_input or not job_posting_input:
                st.error("Please provide both your resume and the job posting.")
            else:
                with st.spinner("🤖 AI agents are crafting your cover letter..."):
                    try:
                        result = run_cover_letter_generation(
                            resume_input,
                            job_posting_input,
                            culture_input or "No specific culture info provided",
                        )
                        st.success("✅ Cover letter generated!")
                        st.markdown("### Your Cover Letter")
                        st.markdown(
                            f'<div class="output-box">{result}</div>',
                            unsafe_allow_html=True,
                        )

                        # Download button
                        st.download_button(
                            label="📥 Download Cover Letter",
                            data=result,
                            file_name="cover_letter.txt",
                            mime="text/plain",
                        )
                    except Exception as e:
                        st.error(f"Error generating cover letter: {str(e)}")

    # ==================== TAB 2: RESUME BUILDER ====================
    with tab2:
        st.markdown("### Build a Tailored Resume")
        st.markdown("Optimize your resume for a specific job posting.")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📋 Your Current Resume")
            old_resume_input = st.text_area(
                "Paste your current resume",
                value=sample_resume if use_sample_data else "",
                height=400,
                key="rb_resume",
            )

        with col2:
            st.markdown("#### 💼 Target Job Description")
            job_desc_input = st.text_area(
                "Paste the job description",
                value=sample_job_posting if use_sample_data else "",
                height=300,
                key="rb_job",
            )

            st.markdown("#### 🏢 Company Background")
            company_bg_input = st.text_area(
                "Company background info",
                value=sample_company_culture if use_sample_data else "",
                height=100,
                key="rb_company",
            )

        if st.button(
            "📄 Generate Tailored Resume",
            key="gen_resume",
            type="primary",
            use_container_width=True,
        ):
            if not old_resume_input or not job_desc_input:
                st.error("Please provide both your resume and the job description.")
            else:
                with st.spinner("🤖 AI agents are optimizing your resume..."):
                    try:
                        result = run_resume_generation(
                            old_resume_input,
                            job_desc_input,
                            company_bg_input or "No specific background provided",
                        )
                        st.success("✅ Resume generated!")
                        st.markdown("### Your Tailored Resume")
                        st.markdown(
                            f'<div class="output-box">{result}</div>',
                            unsafe_allow_html=True,
                        )

                        st.download_button(
                            label="📥 Download Resume",
                            data=result,
                            file_name="tailored_resume.txt",
                            mime="text/plain",
                        )
                    except Exception as e:
                        st.error(f"Error generating resume: {str(e)}")

    # ==================== TAB 3: COMPANY RESEARCH ====================
    with tab3:
        st.markdown("### Research a Company")
        st.markdown(
            "Get insights about company culture, values, and role requirements."
        )

        col1, col2 = st.columns(2)

        with col1:
            company_domain_input = st.text_input(
                "🌐 Company Website",
                value="https://www.agentops.ai" if use_sample_data else "",
                placeholder="https://company.com",
            )

            company_desc_input = st.text_area(
                "📝 Company Description",
                value="We are a software company that builds AI-powered tools for businesses."
                if use_sample_data
                else "",
                height=150,
            )

        with col2:
            hiring_needs_input = st.text_area(
                "💼 Role/Hiring Needs",
                value="We are looking for a software engineer with 3 years of experience in Python and Django."
                if use_sample_data
                else "",
                height=150,
            )

        if st.button(
            "🔍 Research Company",
            key="research",
            type="primary",
            use_container_width=True,
        ):
            if not company_domain_input:
                st.error("Please provide a company website.")
            else:
                with st.spinner("🤖 AI agents are researching the company..."):
                    try:
                        result = run_company_research(
                            company_desc_input, company_domain_input, hiring_needs_input
                        )
                        st.success("✅ Research complete!")
                        st.markdown("### Company Insights")
                        st.markdown(
                            f'<div class="output-box">{result}</div>',
                            unsafe_allow_html=True,
                        )

                        st.download_button(
                            label="📥 Download Research Report",
                            data=result,
                            file_name="company_research.txt",
                            mime="text/plain",
                        )
                    except Exception as e:
                        st.error(f"Error researching company: {str(e)}")

    # ==================== TAB 4: FULL PIPELINE ====================
    with tab4:
        st.markdown("### Full Application Pipeline")
        st.markdown("Run the complete workflow: Research → Cover Letter → Resume")

        st.markdown(
            '<div class="info-box">💡 This runs all agents in sequence to create a complete application package.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📋 Your Resume")
            full_resume_input = st.text_area(
                "Your current resume",
                value=sample_resume if use_sample_data else "",
                height=300,
                key="full_resume",
            )

            st.markdown("#### 🌐 Company Info")
            full_domain_input = st.text_input(
                "Company website",
                value="https://www.agentops.ai" if use_sample_data else "",
                key="full_domain",
            )
            full_desc_input = st.text_area(
                "Company description",
                value="We are a software company that builds AI-powered tools for businesses."
                if use_sample_data
                else "",
                height=100,
                key="full_desc",
            )

        with col2:
            st.markdown("#### 💼 Job Posting")
            full_job_input = st.text_area(
                "Target job posting",
                value=sample_job_posting if use_sample_data else "",
                height=450,
                key="full_job",
            )

        if st.button(
            "🚀 Run Full Pipeline",
            key="full_pipeline",
            type="primary",
            use_container_width=True,
        ):
            if not full_resume_input or not full_job_input:
                st.error("Please provide your resume and the job posting.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                with st.spinner("🤖 Running full application pipeline..."):
                    try:
                        status_text.text("Step 1/3: Researching company...")
                        progress_bar.progress(33)

                        result = run_full_pipeline(
                            full_resume_input,
                            full_job_input,
                            full_domain_input,
                            full_desc_input,
                        )

                        progress_bar.progress(100)
                        status_text.text("Complete!")

                        st.success("✅ Full pipeline complete!")
                        st.markdown("### Application Package")
                        st.markdown(
                            f'<div class="output-box">{result}</div>',
                            unsafe_allow_html=True,
                        )

                        st.download_button(
                            label="📥 Download Full Package",
                            data=result,
                            file_name="application_package.txt",
                            mime="text/plain",
                        )
                    except Exception as e:
                        st.error(f"Error in pipeline: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #9CA3AF;">Built with ❤️ using CrewAI and Streamlit</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
