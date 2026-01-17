#!/usr/bin/env python3
"""
Coding Plan Generator for AI Agents

This script generates comprehensive coding plans for AI agents like Claude Code and Codex,
including architecture, technical definitions, and step-by-step implementation instructions.
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import argparse


class PlanGenerator:
    """Generates comprehensive coding plans for AI agents."""
    
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the coding query to extract requirements and complexity."""
        query_lower = query.lower()
        
        # Determine complexity based on keywords
        complexity_indicators = {
            "simple": ["api", "basic", "simple", "single", "small"],
            "medium": ["application", "system", "multiple", "integrate", "database"],
            "complex": ["architecture", "microservices", "distributed", "scalable", "enterprise"]
        }
        
        complexity = "medium"
        for level, indicators in complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                complexity = level
                break
        
        # Extract key requirements
        requirements = []
        if "api" in query_lower:
            requirements.append("API Development")
        if "database" in query_lower or "db" in query_lower:
            requirements.append("Database Design")
        if "frontend" in query_lower or "ui" in query_lower:
            requirements.append("Frontend Development")
        if "test" in query_lower:
            requirements.append("Testing Framework")
        if "deploy" in query_lower:
            requirements.append("Deployment Strategy")
        
        return {
            "complexity": complexity,
            "requirements": requirements,
            "estimated_time": self._estimate_time(complexity),
            "query": query
        }
    
    def generate_architecture(self, query: str, complexity: str) -> Dict[str, Any]:
        """Generate technical architecture based on query complexity."""
        architectures = {
            "simple": {
                "type": "monolithic",
                "components": ["Single Application", "Configuration"],
                "technologies": ["Node.js/Python", "SQLite/JSON"],
                "description": "Simple single-file application with basic functionality"
            },
            "medium": {
                "type": "layered",
                "components": ["API Layer", "Business Logic", "Data Layer", "Frontend"],
                "technologies": ["React/Vue", "Node.js/Python", "PostgreSQL/MongoDB"],
                "description": "Layered architecture with separation of concerns"
            },
            "complex": {
                "type": "microservices",
                "components": ["API Gateway", "Auth Service", "Business Services", "Database Services", "Frontend"],
                "technologies": ["React/Vue", "Node.js/Python", "PostgreSQL/MongoDB", "Redis", "Docker"],
                "description": "Microservices architecture with distributed components"
            }
        }
        
        return architectures.get(complexity, architectures["medium"])
    
    def define_technical_terms(self, query: str, architecture: Dict[str, Any]) -> Dict[str, str]:
        """Define key technical terms for the project."""
        terms = {
            "API": "Application Programming Interface - allows different software components to communicate",
            "Database": "Organized collection of structured information for data storage and retrieval",
            "Frontend": "User interface and client-side application logic",
            "Backend": "Server-side application logic and data processing",
            "Deployment": "Process of making software available for use in production environment"
        }
        
        # Add architecture-specific terms
        if architecture["type"] == "microservices":
            terms.update({
                "Microservices": "Architectural style that structures an application as a collection of loosely coupled services",
                "API Gateway": "Server that acts as a single entry point for client requests",
                "Service Discovery": "Mechanism for services to find and communicate with each other"
            })
        elif architecture["type"] == "layered":
            terms.update({
                "Layered Architecture": "Organizes application into distinct layers with specific responsibilities",
                "Business Logic": "Rules and calculations that operate on data",
                "Data Access Layer": "Component responsible for interacting with data storage"
            })
        
        return terms
    
    def create_implementation_plan(self, complexity: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Create detailed implementation plan with phases."""
        base_phases = [
            {
                "phase": 1,
                "title": "Foundation Setup",
                "steps": [
                    "Initialize project structure and configuration",
                    "Setup development environment and tools",
                    "Create basic file organization",
                    "Setup version control and project documentation"
                ],
                "duration": "30-60 minutes"
            },
            {
                "phase": 2,
                "title": "Core Implementation",
                "steps": [
                    "Implement main application logic",
                    "Create core components and modules",
                    "Setup data structures and models",
                    "Implement basic functionality"
                ],
                "duration": "1-3 hours"
            },
            {
                "phase": 3,
                "title": "Integration & Testing",
                "steps": [
                    "Integrate different components",
                    "Implement error handling and validation",
                    "Create and run tests",
                    "Performance optimization"
                ],
                "duration": "1-2 hours"
            },
            {
                "phase": 4,
                "title": "Documentation & Deployment",
                "steps": [
                    "Complete documentation and README",
                    "Setup deployment configuration",
                    "Final testing and quality assurance",
                    "Production deployment if required"
                ],
                "duration": "30-60 minutes"
            }
        ]
        
        # Adjust phases based on complexity
        if complexity == "simple":
            # Merge phases for simple projects
            return [
                {
                    "phase": 1,
                    "title": "Implementation",
                    "steps": base_phases[0]["steps"] + base_phases[1]["steps"] + base_phases[2]["steps"],
                    "duration": "1-2 hours"
                }
            ]
        elif complexity == "complex":
            # Add additional phases for complex projects
            base_phases.insert(2, {
                "phase": 3,
                "title": "Service Architecture",
                "steps": [
                    "Design and implement microservices",
                    "Setup service communication",
                    "Implement API gateway",
                    "Configure service discovery"
                ],
                "duration": "2-4 hours"
            })
            # Re-number subsequent phases
            for i, phase in enumerate(base_phases[3:], 3):
                phase["phase"] = i
            return base_phases
        
        return base_phases
    
    def generate_file_structure(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project file structure based on architecture."""
        if architecture["type"] == "simple":
            return {
                "project-root/": {
                    "src/": ["main.py", "utils.py"],
                    "config/": ["settings.py"],
                    "tests/": ["test_main.py"],
                    "README.md": "Project documentation",
                    "requirements.txt": "Python dependencies"
                }
            }
        elif architecture["type"] == "layered":
            return {
                "project-root/": {
                    "src/": {
                        "api/": ["routes.py", "middleware.py"],
                        "business/": ["services.py", "models.py"],
                        "data/": ["database.py", "repositories.py"],
                        "utils/": ["helpers.py", "validators.py"]
                    },
                    "frontend/": ["App.js", "components/"],
                    "tests/": {
                        "unit/": ["test_services.py"],
                        "integration/": ["test_api.py"]
                    },
                    "config/": ["development.py", "production.py"],
                    "docs/": ["api.md", "setup.md"],
                    "README.md": "Project documentation",
                    "requirements.txt": "Python dependencies"
                }
            }
        else:  # microservices
            return {
                "project-root/": {
                    "services/": {
                        "auth-service/": ["app.py", "models.py"],
                        "business-service/": ["app.py", "logic.py"],
                        "data-service/": ["app.py", "database.py"]
                    },
                    "api-gateway/": ["gateway.py", "routes.py"],
                    "frontend/": ["App.js", "components/"],
                    "shared/": ["common.py", "utils.py"],
                    "tests/": {
                        "unit/": ["test_services.py"],
                        "integration/": ["test_gateway.py"],
                        "e2e/": ["test_workflows.py"]
                    },
                    "docker/": ["Dockerfile", "docker-compose.yml"],
                    "config/": ["development.yml", "production.yml"],
                    "docs/": ["architecture.md", "deployment.md"],
                    "README.md": "Project documentation"
                }
            }
    
    def generate_dependencies(self, architecture: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate list of required dependencies."""
        base_deps = {
            "python": ["pytest", "black", "flake8"],
            "javascript": ["eslint", "prettier", "jest"]
        }
        
        if architecture["type"] == "simple":
            return {
                "python": base_deps["python"] + ["flask", "sqlite3"],
                "javascript": base_deps["javascript"] + ["webpack"]
            }
        elif architecture["type"] == "layered":
            return {
                "python": base_deps["python"] + ["flask", "sqlalchemy", "psycopg2", "redis"],
                "javascript": base_deps["javascript"] + ["react", "axios", "webpack"]
            }
        else:  # microservices
            return {
                "python": base_deps["python"] + ["flask", "sqlalchemy", "psycopg2", "redis", "kubernetes"],
                "javascript": base_deps["javascript"] + ["react", "axios", "microfrontend"],
                "infrastructure": ["docker", "kubernetes", "nginx", "postgresql"]
            }
    
    def generate_agent_instructions(self, query: str, complexity: str) -> Dict[str, Any]:
        """Generate specific instructions for different AI agents."""
        claude_instructions = {
            "model": "claude-3-5-sonnet-20241022" if complexity != "simple" else "claude-3-5-haiku-20241022",
            "context_requirements": [
                "Complete implementation plan",
                "Existing codebase structure",
                "Technical requirements and constraints",
                "Testing strategy and validation criteria"
            ],
            "prompts": [
                f"Implement the following based on the plan: {query}",
                "Focus on code quality, error handling, and documentation",
                "Ensure all components follow the specified architecture",
                "Include comprehensive tests for all functionality"
            ],
            "verification_steps": [
                "Review code for adherence to architectural patterns",
                "Validate error handling and edge cases",
                "Ensure proper documentation and comments",
                "Run tests and verify coverage"
            ]
        }
        
        codex_instructions = {
            "model": "gpt-4" if complexity != "simple" else "gpt-3.5-turbo",
            "prompt_templates": [
                "Generate {component} code for {language} with {features}",
                "Create a {test_type} test for {function_name}",
                "Implement {pattern} pattern in {language}"
            ],
            "validation_steps": [
                "Review generated code for syntax and logic errors",
                "Ensure code follows best practices and conventions",
                "Validate integration with existing components",
                "Test functionality and performance"
            ],
            "integration_guidelines": [
                "Generate code in small, testable chunks",
                "Use consistent coding style and patterns",
                "Include proper error handling and validation",
                "Add relevant comments and documentation"
            ]
        }
        
        return {
            "claude_code": claude_instructions,
            "codex": codex_instructions
        }
    
    def _estimate_time(self, complexity: str) -> str:
        """Estimate implementation time based on complexity."""
        time_estimates = {
            "simple": "1-2 hours",
            "medium": "3-6 hours",
            "complex": "1-3 days"
        }
        return time_estimates.get(complexity, "3-6 hours")
    
    def generate_plan(self, query: str) -> Dict[str, Any]:
        """Generate complete coding plan."""
        analysis = self.analyze_query(query)
        architecture = self.generate_architecture(query, analysis["complexity"])
        technical_terms = self.define_technical_terms(query, architecture)
        implementation_plan = self.create_implementation_plan(analysis["complexity"], analysis["requirements"])
        file_structure = self.generate_file_structure(architecture)
        dependencies = self.generate_dependencies(architecture)
        agent_instructions = self.generate_agent_instructions(query, analysis["complexity"])
        
        return {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": self.timestamp,
            "query": query,
            "complexity": analysis["complexity"],
            "estimated_time": analysis["estimated_time"],
            "requirements": analysis["requirements"],
            "architecture": architecture,
            "technical_terms": technical_terms,
            "implementation_plan": implementation_plan,
            "file_structure": file_structure,
            "dependencies": dependencies,
            "agent_instructions": agent_instructions
        }
    
    def format_markdown(self, plan: Dict[str, Any]) -> str:
        """Format the plan as a markdown document."""
        phases_text = []
        for phase in plan['implementation_plan']:
            phase_text = f"""### Phase {phase['phase']}: {phase['title']}
**Duration**: {phase['duration']}
{chr(10).join(f"- {step}" for step in phase['steps'])}"""
            phases_text.append(phase_text)
        
        infrastructure_section = ""
        if plan['dependencies'].get('infrastructure'):
            infrastructure_section = f"""
### Infrastructure
{chr(10).join(f'- {dep}' for dep in plan['dependencies'].get('infrastructure', []))}"""
        
        md = f"""# {plan['query']} - Implementation Plan

## Executive Summary

**Project Overview**: {plan['query']}
**Complexity**: {plan['complexity']}
**Estimated Time**: {plan['estimated_time']}
**Requirements**: {', '.join(plan['requirements']) if plan['requirements'] else 'General development'}

## Technical Architecture

**Architecture Type**: {plan['architecture']['type']}
**Description**: {plan['architecture']['description']}

### Components
{chr(10).join(f"- **{comp}**" for comp in plan['architecture']['components'])}

### Technology Stack
{chr(10).join(f"- **{tech}**" for tech in plan['architecture']['technologies'])}

## Technical Terms & Definitions

{chr(10).join(f"- **{term}**: {definition}" for term, definition in plan['technical_terms'].items())}

## Implementation Plan

{chr(10).join(phases_text)}

## File Structure

```
{self._format_file_structure(plan['file_structure'])}
```

## Dependencies

### Python
{chr(10).join(f"- {dep}" for dep in plan['dependencies']['python'])}

### JavaScript
{chr(10).join(f"- {dep}" for dep in plan['dependencies']['javascript'])}
{infrastructure_section}

## AI Agent Instructions

### For Claude Code
**Recommended Model**: {plan['agent_instructions']['claude_code']['model']}

**Context Requirements**:
{chr(10).join(f"- {req}" for req in plan['agent_instructions']['claude_code']['context_requirements'])}

**Key Prompts**:
{chr(10).join(f"- {prompt}" for prompt in plan['agent_instructions']['claude_code']['prompts'])}

**Verification Steps**:
{chr(10).join(f"- {step}" for step in plan['agent_instructions']['claude_code']['verification_steps'])}

### For Codex/OpenAI
**Recommended Model**: {plan['agent_instructions']['codex']['model']}

**Prompt Templates**:
{chr(10).join(f"- {template}" for template in plan['agent_instructions']['codex']['prompt_templates'])}

**Validation Steps**:
{chr(10).join(f"- {step}" for step in plan['agent_instructions']['codex']['validation_steps'])}

**Integration Guidelines**:
{chr(10).join(f"- {guideline}" for guideline in plan['agent_instructions']['codex']['integration_guidelines'])}

---
*Generated on {plan['timestamp']}*
*Plan ID: {plan['plan_id']}*
"""
        return md
    
    def _format_file_structure(self, structure: Dict[str, Any], indent: int = 0) -> str:
        """Recursively format file structure as tree."""
        lines = []
        for key, value in structure.items():
            if isinstance(value, dict):
                lines.append("  " * indent + key + "/")
                lines.append(self._format_file_structure(value, indent + 1))
            elif isinstance(value, list):
                lines.append("  " * indent + key + "/")
                for item in value:
                    lines.append("  " * (indent + 1) + item)
            else:
                lines.append("  " * indent + key)
        return chr(10).join(lines)


def main():
    """Main function to run the plan generator."""
    parser = argparse.ArgumentParser(description="Generate comprehensive coding plans for AI agents")
    parser.add_argument("query", help="The coding query or project description")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    generator = PlanGenerator()
    plan = generator.generate_plan(args.query)
    
    if args.format == "json":
        output = json.dumps(plan, indent=2)
    else:
        output = generator.format_markdown(plan)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Plan saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
