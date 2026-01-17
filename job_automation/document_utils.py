"""
Document Export and Management Utilities
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import re


class ApplicationTracker:
    """Track and analyze job applications"""
    
    def __init__(self, storage_path: str = "job_automation_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.applications_file = self.storage_path / "applications.json"
        self.templates_file = self.storage_path / "templates.json"
        self.history_file = self.storage_path / "history.json"
    
    def save_application(self, application_data: Dict[str, Any]) -> str:
        """Save a job application record"""
        applications = self.load_applications()
        
        # Generate unique ID
        app_id = hashlib.md5(
            f"{application_data.get('company', '')}{application_data.get('position', '')}{datetime.now()}".encode()
        ).hexdigest()[:8]
        
        application_data['id'] = app_id
        application_data['date_applied'] = datetime.now().isoformat()
        application_data['status'] = application_data.get('status', 'Applied')
        
        applications[app_id] = application_data
        
        with open(self.applications_file, 'w') as f:
            json.dump(applications, f, indent=2)
        
        return app_id
    
    def load_applications(self) -> Dict[str, Any]:
        """Load all applications"""
        if self.applications_file.exists():
            with open(self.applications_file, 'r') as f:
                return json.load(f)
        return {}
    
    def update_application_status(self, app_id: str, status: str, notes: str = "") -> bool:
        """Update application status"""
        applications = self.load_applications()
        
        if app_id in applications:
            applications[app_id]['status'] = status
            applications[app_id]['last_updated'] = datetime.now().isoformat()
            if notes:
                applications[app_id]['notes'] = applications[app_id].get('notes', [])
                applications[app_id]['notes'].append({
                    'date': datetime.now().isoformat(),
                    'note': notes
                })
            
            with open(self.applications_file, 'w') as f:
                json.dump(applications, f, indent=2)
            return True
        return False
    
    def get_application_stats(self) -> Dict[str, Any]:
        """Get statistics about applications"""
        applications = self.load_applications()
        
        if not applications:
            return {
                'total': 0,
                'by_status': {},
                'response_rate': 0,
                'interview_rate': 0
            }
        
        stats = {
            'total': len(applications),
            'by_status': {},
            'by_company': {},
            'by_month': {},
        }
        
        for app in applications.values():
            # Status counts
            status = app.get('status', 'Unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Company counts
            company = app.get('company', 'Unknown')
            stats['by_company'][company] = stats['by_company'].get(company, 0) + 1
            
            # Monthly counts
            date = app.get('date_applied', '')
            if date:
                month = date[:7]  # YYYY-MM format
                stats['by_month'][month] = stats['by_month'].get(month, 0) + 1
        
        # Calculate rates
        responded = sum(1 for app in applications.values() 
                       if app.get('status') not in ['Applied', 'Unknown'])
        stats['response_rate'] = (responded / len(applications)) * 100 if applications else 0
        
        interviewed = sum(1 for app in applications.values() 
                         if 'interview' in app.get('status', '').lower())
        stats['interview_rate'] = (interviewed / len(applications)) * 100 if applications else 0
        
        return stats
    
    def save_template(self, template_name: str, template_type: str, content: str) -> bool:
        """Save a reusable template"""
        templates = self.load_templates()
        
        templates[template_name] = {
            'type': template_type,
            'content': content,
            'created': datetime.now().isoformat(),
            'last_used': None,
            'use_count': 0
        }
        
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        
        return True
    
    def load_templates(self) -> Dict[str, Any]:
        """Load saved templates"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        return {}


class JobMatchScorer:
    """Calculate job match scores and provide analysis"""
    
    @staticmethod
    def calculate_match_score(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate detailed match score between resume and job description"""
        
        # Extract keywords from job description
        job_keywords = JobMatchScorer._extract_keywords(job_description)
        resume_keywords = JobMatchScorer._extract_keywords(resume_text)
        
        # Calculate different aspects of match
        skills_match = JobMatchScorer._calculate_skills_match(resume_keywords, job_keywords)
        experience_match = JobMatchScorer._calculate_experience_match(resume_text, job_description)
        education_match = JobMatchScorer._calculate_education_match(resume_text, job_description)
        
        # Overall score
        overall_score = (
            skills_match['score'] * 0.5 +
            experience_match['score'] * 0.3 +
            education_match['score'] * 0.2
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'skills_match': skills_match,
            'experience_match': experience_match,
            'education_match': education_match,
            'missing_keywords': list(job_keywords - resume_keywords),
            'matching_keywords': list(job_keywords & resume_keywords),
            'recommendations': JobMatchScorer._generate_recommendations(
                overall_score, skills_match, experience_match, education_match
            )
        }
    
    @staticmethod
    def _extract_keywords(text: str) -> set:
        """Extract relevant keywords from text"""
        # Common tech skills and keywords
        tech_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node', 'express', 'django', 'flask', 'fastapi', 'spring', 'sql', 'nosql',
            'mongodb', 'postgresql', 'mysql', 'redis', 'aws', 'azure', 'gcp', 'docker',
            'kubernetes', 'terraform', 'ansible', 'jenkins', 'git', 'github', 'gitlab',
            'ci/cd', 'devops', 'agile', 'scrum', 'kanban', 'jira', 'api', 'rest',
            'graphql', 'microservices', 'serverless', 'machine learning', 'deep learning',
            'data science', 'data analysis', 'data engineering', 'etl', 'spark', 'hadoop',
            'tableau', 'power bi', 'excel', 'project management', 'product management',
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'strategic thinking', 'stakeholder management', 'customer service'
        ]
        
        text_lower = text.lower()
        found_keywords = set()
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                found_keywords.add(keyword)
        
        # Extract years of experience
        years_pattern = r'(\d+)\+?\s*years?'
        years_matches = re.findall(years_pattern, text_lower)
        for match in years_matches:
            found_keywords.add(f"{match}_years_experience")
        
        # Extract education levels
        education_keywords = ['phd', 'doctorate', 'master', 'mba', 'bachelor', 'bs', 'ba', 'associate']
        for edu in education_keywords:
            if edu in text_lower:
                found_keywords.add(f"education_{edu}")
        
        return found_keywords
    
    @staticmethod
    def _calculate_skills_match(resume_skills: set, job_skills: set) -> Dict[str, Any]:
        """Calculate skills match percentage"""
        if not job_skills:
            return {'score': 100, 'matched': 0, 'total': 0}
        
        matched = len(resume_skills & job_skills)
        total = len(job_skills)
        score = (matched / total) * 100 if total > 0 else 0
        
        return {
            'score': round(score, 1),
            'matched': matched,
            'total': total,
            'matched_skills': list(resume_skills & job_skills)[:10],  # Top 10 matches
            'missing_skills': list(job_skills - resume_skills)[:10]  # Top 10 missing
        }
    
    @staticmethod
    def _calculate_experience_match(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate experience match"""
        # Extract years of experience from job description
        job_years_pattern = r'(\d+)\+?\s*years?'
        job_matches = re.findall(job_years_pattern, job_description.lower())
        required_years = int(job_matches[0]) if job_matches else 0
        
        # Extract years from resume
        resume_matches = re.findall(job_years_pattern, resume_text.lower())
        candidate_years = max([int(m) for m in resume_matches]) if resume_matches else 0
        
        if required_years == 0:
            score = 100
        elif candidate_years >= required_years:
            score = 100
        else:
            score = (candidate_years / required_years) * 100 if required_years > 0 else 0
        
        return {
            'score': round(score, 1),
            'required': required_years,
            'candidate': candidate_years
        }
    
    @staticmethod
    def _calculate_education_match(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate education match"""
        education_levels = {
            'phd': 4, 'doctorate': 4,
            'master': 3, 'mba': 3,
            'bachelor': 2, 'bs': 2, 'ba': 2,
            'associate': 1
        }
        
        # Find highest education in job description
        job_edu = 0
        job_edu_name = "Not specified"
        for level, value in education_levels.items():
            if level in job_description.lower():
                if value > job_edu:
                    job_edu = value
                    job_edu_name = level.upper()
        
        # Find highest education in resume
        resume_edu = 0
        resume_edu_name = "Not found"
        for level, value in education_levels.items():
            if level in resume_text.lower():
                if value > resume_edu:
                    resume_edu = value
                    resume_edu_name = level.upper()
        
        if job_edu == 0:
            score = 100
        elif resume_edu >= job_edu:
            score = 100
        else:
            score = (resume_edu / job_edu) * 100 if job_edu > 0 else 0
        
        return {
            'score': round(score, 1),
            'required': job_edu_name,
            'candidate': resume_edu_name,
            'meets_requirement': resume_edu >= job_edu
        }
    
    @staticmethod
    def _generate_recommendations(overall_score: float, skills: Dict, 
                                 experience: Dict, education: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if overall_score >= 85:
            recommendations.append("🎯 Excellent match! Your profile strongly aligns with this role.")
            recommendations.append("Focus on customizing your cover letter to highlight your fit.")
        elif overall_score >= 70:
            recommendations.append("✅ Good match! You meet most of the requirements.")
            recommendations.append("Emphasize your matching skills in your application.")
        else:
            recommendations.append("⚠️ Moderate match. Consider gaining additional skills or experience.")
        
        if skills['score'] < 70:
            missing_count = skills['total'] - skills['matched']
            recommendations.append(f"📚 Skills Gap: Add {missing_count} more relevant skills to your resume.")
            if 'missing_skills' in skills and skills['missing_skills']:
                top_missing = ', '.join(skills['missing_skills'][:3])
                recommendations.append(f"Priority skills to acquire: {top_missing}")
        
        if experience['score'] < 100 and experience['required'] > 0:
            gap = experience['required'] - experience['candidate']
            recommendations.append(f"💼 Experience Gap: {gap} more year(s) of experience would strengthen your application.")
            recommendations.append("Highlight transferable skills and achievements to compensate.")
        
        if not education['meets_requirement']:
            recommendations.append(f"🎓 Education: Consider certifications or courses to meet the {education['required']} requirement.")
        
        # Always provide actionable next steps
        recommendations.append("\n📋 Next Steps:")
        recommendations.append("1. Update resume with missing keywords")
        recommendations.append("2. Tailor cover letter to address any gaps")
        recommendations.append("3. Prepare examples demonstrating relevant skills")
        
        return recommendations


class DocumentExporter:
    """Simple document export functionality"""
    
    @staticmethod
    def export_to_txt(content: Dict[str, str], filename: str) -> str:
        """Export content to plain text file"""
        output_path = f"exports/{filename}.txt"
        os.makedirs("exports", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Title
            if 'title' in content:
                f.write(f"{'='*60}\n")
                f.write(f"{content['title'].center(60)}\n")
                f.write(f"{'='*60}\n\n")
            
            # Content sections
            for section_name, section_content in content.items():
                if section_name != 'title':
                    f.write(f"\n{'-'*40}\n")
                    f.write(f"{section_name.replace('_', ' ').upper()}\n")
                    f.write(f"{'-'*40}\n\n")
                    
                    if isinstance(section_content, str):
                        f.write(section_content)
                        f.write("\n\n")
        
        return output_path
    
    @staticmethod
    def export_to_markdown(content: Dict[str, str], filename: str) -> str:
        """Export content to Markdown file"""
        output_path = f"exports/{filename}.md"
        os.makedirs("exports", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Title
            if 'title' in content:
                f.write(f"# {content['title']}\n\n")
            
            # Content sections
            for section_name, section_content in content.items():
                if section_name != 'title':
                    f.write(f"## {section_name.replace('_', ' ').title()}\n\n")
                    
                    if isinstance(section_content, str):
                        f.write(section_content)
                        f.write("\n\n")
        
        return output_path