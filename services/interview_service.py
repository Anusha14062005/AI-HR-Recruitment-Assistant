import json
import logging
from typing import Dict, Any, List
from config import Config
from services.ai_service import AIService

logger = logging.getLogger("InterviewService")

class InterviewService:
    """Personalized interview question generator supporting AI LLM and DEMO_MODE fallback."""

    @classmethod
    def generate_questions(cls, candidate_data: Dict[str, Any], job_data: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        """Generate personalized interview questions across 6 core categories."""
        cand_name = candidate_data.get('name', 'Candidate')
        cand_skills = [s.get('skill_name', s) if isinstance(s, dict) else str(s) for s in candidate_data.get('skills', [])]
        cand_projects = [p.get('project_title', 'Core Project') for p in candidate_data.get('projects', [])]
        job_title = job_data.get('title', 'Software Engineer')
        missing_skills = candidate_data.get('missing_skills', [])

        # Check if external AI provider is configured
        if not Config.DEMO_MODE and Config.AI_API_KEY:
            prompt = f"""
            Generate exactly {count} personalized interview questions for:
            Candidate Name: {cand_name}
            Applying For: {job_title}
            Candidate Skills: {', '.join(cand_skills[:8])}
            Candidate Projects: {', '.join(cand_projects[:3])}
            Missing Skills from Job Requirements: {', '.join(missing_skills) if missing_skills else 'None'}
            Job Responsibilities: {job_data.get('responsibilities', '')}

            Return a valid JSON array of objects with schema:
            [
                {{
                    "category": "Technical | Project-Based | Behavioral | Situational | Role-Specific | Skill Gap",
                    "difficulty": "Easy | Medium | Hard",
                    "question_text": "The actual personalized interview question",
                    "expected_skills": "Skills, concepts, or keywords expected in the answer"
                }}
            ]
            """
            raw = AIService.call_llm(prompt, "You are a senior tech hiring manager and interview designer. Output valid JSON only.")
            if raw:
                try:
                    cleaned = AIService._clean_json_markdown(raw)
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed[:count]
                except Exception as e:
                    logger.warning(f"Failed to parse LLM interview questions: {e}")

        # Fallback offline generator
        return cls._generate_offline_questions(candidate_data, job_data, count)

    @classmethod
    def _generate_offline_questions(cls, candidate_data: Dict[str, Any], job_data: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        cand_skills = [s.get('skill_name', s) if isinstance(s, dict) else str(s) for s in candidate_data.get('skills', [])]
        cand_projects = candidate_data.get('projects', [])
        primary_project = cand_projects[0].get('project_title', 'Key Enterprise System') if cand_projects else "your recent production system"
        missing_skills = candidate_data.get('missing_skills', [])
        job_title = job_data.get('title', 'Software Engineer')

        pool = [
            # Technical Questions
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question_text": f"How do you approach database schema design and indexing in {cand_skills[0] if cand_skills else 'relational databases'} when optimizing for high read/write concurrency?",
                "expected_skills": f"{cand_skills[0] if cand_skills else 'Database'}, Indexing, Concurrency, Query Optimization"
            },
            {
                "category": "Technical",
                "difficulty": "Hard",
                "question_text": "Explain how connection pooling works under heavy load and how you prevent resource starvation between backend workers and the database layer.",
                "expected_skills": "Connection Pooling, Thread Safety, Timeout Handling"
            },
            {
                "category": "Technical",
                "difficulty": "Easy",
                "question_text": "What are the core differences between monolithic and microservice architectures, and what trade-offs have you experienced in production?",
                "expected_skills": "System Architecture, Network Latency, Scalability"
            },

            # Project-Based Questions
            {
                "category": "Project-Based",
                "difficulty": "Medium",
                "question_text": f"In your project '{primary_project}', what was the most difficult architectural bottleneck you encountered and how did you resolve it?",
                "expected_skills": "Problem Solving, Performance Debugging, Architectural Decision-Making"
            },
            {
                "category": "Project-Based",
                "difficulty": "Hard",
                "question_text": f"Walk us through how you handled state management, data integrity, and automated unit testing in '{primary_project}'.",
                "expected_skills": "Testing Strategy, Data Integrity, Software Lifecycle"
            },

            # Behavioral Questions
            {
                "category": "Behavioral",
                "difficulty": "Medium",
                "question_text": "Describe a scenario where you disagreed with a tech lead or product manager regarding technical debt versus delivery speed. How did you align and move forward?",
                "expected_skills": "Constructive Conflict Resolution, Communication, Stakeholder Alignment"
            },
            {
                "category": "Behavioral",
                "difficulty": "Easy",
                "question_text": "Tell us about a time you made an error in production or missed a critical bug during code review. What steps did you take to mitigate the impact?",
                "expected_skills": "Accountability, Incident Post-Mortem, Continuous Improvement"
            },

            # Situational Questions
            {
                "category": "Situational",
                "difficulty": "Hard",
                "question_text": f"If an API endpoint for {job_title} suddenly experiences a 5x surge in p99 response times during peak hours, what is your systematic troubleshooting checklist?",
                "expected_skills": "Observability, Log Tracing, Profiling, CPU/Memory Analysis"
            },
            {
                "category": "Situational",
                "difficulty": "Medium",
                "question_text": "If you are assigned a legacy codebase with zero automated tests and asked to ship a critical feature in two weeks, how do you prioritize safety and delivery?",
                "expected_skills": "Risk Management, Regression Testing, Refactoring"
            },

            # Role-Specific Questions
            {
                "category": "Role-Specific",
                "difficulty": "Medium",
                "question_text": f"What coding standards, linting rules, and CI/CD gates would you advocate implementing for our {job_title} team?",
                "expected_skills": "DevOps, Code Quality, CI/CD, Engineering Culture"
            },
            {
                "category": "Role-Specific",
                "difficulty": "Hard",
                "question_text": f"How do you design RESTful interfaces to remain backwards-compatible while evolving new business capabilities?",
                "expected_skills": "API Versioning, Backward Compatibility, Schema Evolution"
            }
        ]

        # Skill Gap Questions (High Priority if missing skills exist)
        skill_gap_pool = []
        if missing_skills:
            for ms in missing_skills[:2]:
                skill_gap_pool.append({
                    "category": "Skill Gap",
                    "difficulty": "Medium",
                    "question_text": f"Our job requirements specify experience with {ms}, which is not prominent on your resume. How would you quickly ramp up on {ms} and what adjacent technologies have you mastered?",
                    "expected_skills": f"{ms}, Self-Directed Learning, Transferable Technical Skills"
                })
        else:
            skill_gap_pool.append({
                "category": "Skill Gap",
                "difficulty": "Medium",
                "question_text": "Your profile covers our core requirements thoroughly. What emerging technical skill or cloud tool are you currently studying to stay ahead?",
                "expected_skills": "Continuous Learning, Technology Horizons"
            })

        # Assemble prioritized selection
        combined = skill_gap_pool + pool
        # Loop or slice to meet requested count
        while len(combined) < count:
            combined.extend(pool)

        return combined[:count]

    @classmethod
    def export_questions_text(cls, questions: List[Dict[str, Any]], candidate_name: str, job_title: str) -> str:
        """Format questions into a clean text document."""
        output = [
            "=" * 70,
            f"  AI-GENERATED INTERVIEW QUESTIONS",
            f"  Candidate: {candidate_name}",
            f"  Position:  {job_title}",
            "=" * 70,
            ""
        ]
        for i, q in enumerate(questions, 1):
            output.append(f"[{i}] [{q.get('category', 'Technical')}] (Difficulty: {q.get('difficulty', 'Medium')})")
            output.append(f"Q: {q.get('question_text')}")
            if q.get('expected_skills'):
                output.append(f"Expected Concepts: {q.get('expected_skills')}")
            output.append("-" * 70)
            output.append("")
        return "\n".join(output)

