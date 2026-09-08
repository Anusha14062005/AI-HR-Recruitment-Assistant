import re
from typing import Dict, Any, List
from services.resume_parser import TECH_SKILLS

def parse_job_description_offline(title: str, description: str, responsibilities: str = "") -> Dict[str, Any]:
    """Offline deterministic analyzer for Job Descriptions."""
    combined_text = f"{title}\n{description}\n{responsibilities}".lower()
    
    # 1. Detect required skills
    detected_skills = []
    for skill_name in TECH_SKILLS.keys():
        pattern = r'\b' + re.escape(skill_name.lower()) + r'\b'
        if re.search(pattern, combined_text):
            detected_skills.append(skill_name)
            
    # If no skills detected, supply sensible defaults based on title
    if not detected_skills:
        if "frontend" in combined_text or "react" in combined_text:
            detected_skills = ["React", "JavaScript", "HTML5", "CSS3", "Git"]
        elif "python" in combined_text or "backend" in combined_text:
            detected_skills = ["Python", "Flask", "MySQL", "REST API", "Git"]
        elif "devops" in combined_text or "cloud" in combined_text:
            detected_skills = ["Docker", "Kubernetes", "AWS", "Linux", "CI/CD"]
        elif "machine learning" in combined_text or "ai" in combined_text:
            detected_skills = ["Python", "PyTorch", "NLP", "Scikit-Learn", "Docker"]
        else:
            detected_skills = ["Python", "SQL", "Git"]

    # Partition into required vs preferred
    split_idx = max(1, int(len(detected_skills) * 0.7))
    required_skills = detected_skills[:split_idx]
    preferred_skills = detected_skills[split_idx:] if split_idx < len(detected_skills) else ["Docker", "AWS"]

    # 2. Extract years of experience
    exp_years = 3.0
    exp_match = re.search(r'(\d+)(?:\s*[-–]\s*\d+)?\s*\+?\s*(?:years?|yrs?)', combined_text)
    if exp_match:
        try:
            exp_years = float(exp_match.group(1))
        except Exception:
            exp_years = 3.0

    # 3. Extract education requirements
    edu = "Bachelor's degree in Computer Science, Software Engineering, or equivalent practical experience."
    if "master" in combined_text or "ph.d" in combined_text:
        edu = "Master's or Ph.D. in Computer Science, Artificial Intelligence, or related technical field."

    # 4. Extract responsibilities
    resp_list = []
    if responsibilities:
        resp_list = [r.strip() for r in responsibilities.splitlines() if r.strip()]
    if not resp_list:
        resp_list = [
            f"Design, build, and deploy production-grade software using {', '.join(required_skills[:3])}.",
            "Collaborate cross-functionally with product managers, QA, and infrastructure teams.",
            "Conduct peer code reviews and maintain high standards of code test coverage and documentation.",
            "Monitor production performance metrics and proactively resolve system bottlenecks."
        ]

    # 5. Extract keywords
    keywords = list(set(required_skills + ["Scalability", "Microservices", "REST API", "Testing", "Agile"]))

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_required_years": exp_years,
        "education_requirements": edu,
        "responsibilities": resp_list,
        "keywords": keywords[:8]
    }

