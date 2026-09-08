import os
import re
import json
import logging
import requests
from config import Config

logger = logging.getLogger("AIService")

class AIService:
    """Unified AI service supporting Gemini, OpenAI, Ollama, and full offline DEMO_MODE."""

    @staticmethod
    def _clean_json_markdown(raw_text: str) -> str:
        """Strip markdown code fences (```json ... ```) from LLM output."""
        if not raw_text:
            return "{}"
        cleaned = re.sub(r'^```(?:json)?\s*', '', raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned.strip(), flags=re.MULTILINE)
        return cleaned.strip()

    @classmethod
    def call_llm(cls, prompt: str, system_instruction: str = "") -> str:
        """Dispatch prompt to configured provider if DEMO_MODE is False."""
        if Config.DEMO_MODE or not Config.AI_API_KEY:
            logger.info("DEMO_MODE active or no API key provided. Using built-in AI engine.")
            return ""

        provider = Config.AI_PROVIDER.lower()
        try:
            if 'gemini' in provider:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.AI_MODEL}:generateContent?key={Config.AI_API_KEY}"
                payload = {
                    "contents": [{
                        "parts": [{"text": f"{system_instruction}\n\n{prompt}" if system_instruction else prompt}]
                    }],
                    "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
                }
                res = requests.post(url, json=payload, timeout=25)
                res.raise_for_status()
                data = res.json()
                return data['candidates'][0]['content']['parts'][0]['text']

            elif 'openai' in provider:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {Config.AI_API_KEY}", "Content-Type": "application/json"}
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                payload = {
                    "model": Config.AI_MODEL if "gpt" in Config.AI_MODEL else "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"}
                }
                res = requests.post(url, headers=headers, json=payload, timeout=25)
                res.raise_for_status()
                data = res.json()
                return data['choices'][0]['message']['content']

            elif 'ollama' in provider:
                url = "http://localhost:11434/api/generate"
                payload = {
                    "model": Config.AI_MODEL or "llama3",
                    "prompt": f"{system_instruction}\n\n{prompt}",
                    "stream": False,
                    "format": "json"
                }
                res = requests.post(url, json=payload, timeout=30)
                res.raise_for_status()
                return res.json().get('response', '')

        except Exception as e:
            logger.warning(f"AI API call to '{provider}' failed ({e}). Reverting to fallback demo engine.")
            return ""

        return ""

    @classmethod
    def analyze_resume_text(cls, resume_text: str) -> dict:
        """Extract structured profile from resume text."""
        # Check if external AI provider is configured and not in demo mode
        if not Config.DEMO_MODE and Config.AI_API_KEY:
            prompt = f"""
            Analyze the following resume text and output a valid JSON object matching this schema:
            {{
                "name": "Candidate Full Name",
                "email": "email address",
                "phone": "phone number",
                "location": "City, State/Country",
                "current_title": "Current or most recent job title",
                "years_experience": 4.5,
                "education": [
                    {{"degree": "B.S. in CS", "institution": "University Name", "field_of_study": "Computer Science", "graduation_year": "2021", "grade": "3.8 GPA"}}
                ],
                "experience": [
                    {{"company": "Company Name", "title": "Role Title", "start_date": "2022-01", "end_date": "Present", "is_current": true, "description": "Key contributions"}}
                ],
                "skills": [
                    {{"skill_name": "Python", "category": "Programming Language", "proficiency": "Expert"}}
                ],
                "projects": [
                    {{"project_title": "Project Name", "description": "Summary", "technologies_used": "Python, Docker"}}
                ],
                "certifications": [
                    {{"name": "AWS Certified Developer", "issuing_organization": "Amazon Web Services", "issue_date": "2023"}}
                ],
                "achievements": [
                    "Won Hackathon 2023", "Reduced latency by 40%"
                ],
                "summary": "Concise executive overview of candidate qualifications."
            }}

            Resume Text:
            {resume_text[:6000]}
            """
            raw_response = cls.call_llm(prompt, "You are a professional HR resume parsing assistant. Return ONLY valid JSON.")
            if raw_response:
                try:
                    parsed = json.loads(cls._clean_json_markdown(raw_response))
                    if isinstance(parsed, dict) and parsed.get('name'):
                        return parsed
                except Exception as e:
                    logger.warning(f"Failed to parse LLM resume response as JSON: {e}")

        # Fallback to local intelligent extractor
        from services.resume_parser import extract_resume_entities
        return extract_resume_entities(resume_text)

    @classmethod
    def analyze_job_description(cls, title: str, description: str, responsibilities: str = "") -> dict:
        """Extract structured skills, experience, and requirements from Job Description."""
        if not Config.DEMO_MODE and Config.AI_API_KEY:
            prompt = f"""
            Extract requirements from this Job Description into a JSON object:
            {{
                "required_skills": ["Python", "Flask", "MySQL"],
                "preferred_skills": ["Redis", "Docker", "AWS"],
                "experience_required_years": 4.0,
                "education_requirements": "Bachelor's in CS or equivalent",
                "responsibilities": ["Design APIs", "Database optimization"],
                "keywords": ["REST", "Microservices", "Scalability"]
            }}

            Job Title: {title}
            Description: {description}
            Responsibilities: {responsibilities}
            """
            raw_response = cls.call_llm(prompt, "You are an HR JD analyzer. Return ONLY valid JSON.")
            if raw_response:
                try:
                    parsed = json.loads(cls._clean_json_markdown(raw_response))
                    if isinstance(parsed, dict) and 'required_skills' in parsed:
                        return parsed
                except Exception as e:
                    logger.warning(f"Failed to parse LLM JD analysis: {e}")

        # Fallback to local analyzer
        from services.job_analyzer import parse_job_description_offline
        return parse_job_description_offline(title, description, responsibilities)

