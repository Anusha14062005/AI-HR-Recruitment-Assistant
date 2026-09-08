import re
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("MatchingService")

SKILL_SYNONYMS = {
    "rest api": ["rest", "api", "apis", "fastapi", "flask", "django"],
    "mysql": ["sql", "mariadb", "postgresql", "relational database", "rdbms"],
    "postgresql": ["sql", "mysql", "postgres", "rdbms"],
    "docker": ["containers", "containerization", "docker-compose", "kubernetes"],
    "kubernetes": ["k8s", "docker", "orchestration"],
    "aws": ["amazon web services", "cloud", "ec2", "s3"],
    "gcp": ["google cloud", "cloud"],
    "react": ["react.js", "reactjs", "frontend", "next.js"],
    "vue": ["vue.js", "vuejs"],
    "python": ["python3", "flask", "django", "fastapi"],
    "javascript": ["js", "typescript", "es6", "node.js"],
    "typescript": ["ts", "javascript"],
    "ci/cd": ["continuous integration", "github actions", "jenkins", "gitlab ci"]
}

def compute_match(candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transparent 5-Factor Weighted Matching Algorithm:
    1. Skills Match: 50%
    2. Experience Match: 20%
    3. Education Match: 10%
    4. Project Relevance: 10%
    5. Preferred Skills: 10%
    """
    # 1. Candidate skills normalization
    raw_cand_skills = candidate_data.get('skills', [])
    cand_skill_names = set()
    for s in raw_cand_skills:
        if isinstance(s, dict):
            cand_skill_names.add(s.get('skill_name', '').strip().lower())
        elif isinstance(s, str):
            cand_skill_names.add(s.strip().lower())

    # Candidate text pool (resume text, experience, projects)
    cand_corpus = (
        candidate_data.get('extracted_text', '') + " " +
        candidate_data.get('ai_summary', '') + " " +
        " ".join([p.get('project_title', '') + " " + p.get('description', '') + " " + p.get('technologies_used', '') 
                  for p in candidate_data.get('projects', [])]) + " " +
        " ".join([e.get('title', '') + " " + e.get('description', '') 
                  for e in candidate_data.get('experience', [])])
    ).lower()

    # 2. Job skills normalization
    required_skills_raw = job_data.get('required_skills', [])
    preferred_skills_raw = job_data.get('preferred_skills', [])

    matched_skills = []
    missing_skills = []
    partial_skills = []

    # Calculate Skills Match (50%)
    req_match_points = 0.0
    for req_skill in required_skills_raw:
        r_lower = req_skill.strip().lower()
        if r_lower in cand_skill_names or re.search(r'\b' + re.escape(r_lower) + r'\b', cand_corpus):
            matched_skills.append(req_skill)
            req_match_points += 1.0
        else:
            # Check synonyms for partial match
            synonyms = SKILL_SYNONYMS.get(r_lower, [])
            partial_found = False
            for syn in synonyms:
                if syn in cand_skill_names or syn in cand_corpus:
                    partial_skills.append(req_skill)
                    req_match_points += 0.5
                    partial_found = True
                    break
            if not partial_found:
                missing_skills.append(req_skill)

    total_required = max(1, len(required_skills_raw))
    skills_score = min(100.0, (req_match_points / total_required) * 100.0)

    # 3. Calculate Preferred Skills Match (10%)
    pref_match_points = 0.0
    if preferred_skills_raw:
        for pref_skill in preferred_skills_raw:
            p_lower = pref_skill.strip().lower()
            if p_lower in cand_skill_names or p_lower in cand_corpus:
                pref_match_points += 1.0
        preferred_score = min(100.0, (pref_match_points / max(1, len(preferred_skills_raw))) * 100.0)
    else:
        preferred_score = 100.0

    # 4. Calculate Experience Match (20%)
    cand_exp = float(candidate_data.get('years_experience', 3.0))
    job_exp_req = float(job_data.get('experience_required_years', 3.0))
    if cand_exp >= job_exp_req:
        experience_score = 100.0
    else:
        ratio = cand_exp / max(1.0, job_exp_req)
        experience_score = max(40.0, min(95.0, ratio * 100.0))

    # 5. Calculate Education Match (10%)
    education_score = 85.0
    edu_list = candidate_data.get('education', [])
    cand_edu_text = " ".join([str(e) for e in edu_list]).lower()
    if any(deg in cand_edu_text for deg in ["master", "m.s.", "ph.d.", "doctorate"]):
        education_score = 100.0
    elif any(deg in cand_edu_text for deg in ["bachelor", "b.s.", "b.tech", "degree"]):
        education_score = 90.0
    elif "computer science" in cand_edu_text or "engineering" in cand_edu_text:
        education_score = 90.0

    # 6. Calculate Project / Domain Relevance (10%)
    project_score = 75.0
    projects = candidate_data.get('projects', [])
    if projects:
        project_hits = 0
        for p in projects:
            p_text = (p.get('project_title', '') + " " + p.get('description', '') + " " + p.get('technologies_used', '')).lower()
            if any(r.strip().lower() in p_text for r in required_skills_raw):
                project_hits += 1
        if project_hits >= 2:
            project_score = 95.0
        elif project_hits == 1:
            project_score = 85.0

    # 7. Compute Overall Weighted Score
    overall_score = round(
        (skills_score * 0.50) +
        (experience_score * 0.20) +
        (education_score * 0.10) +
        (project_score * 0.10) +
        (preferred_score * 0.10),
        1
    )

    # 8. Recommendation Categorization
    if overall_score >= 85.0:
        recommendation = "Strong Match"
    elif overall_score >= 70.0:
        recommendation = "Potential Match"
    else:
        recommendation = "Needs Review"

    # 9. Strengths, Weaknesses, and AI Explanation
    cand_name = candidate_data.get('name', 'Candidate')
    job_title = job_data.get('title', 'Role')

    strengths = (
        f"Strong proficiency demonstrated in {', '.join(matched_skills[:4]) if matched_skills else 'core competencies'}. "
        f"Candidate offers {cand_exp} years of industry experience with relevant project background."
    )
    if missing_skills:
        weaknesses = (
            f"Missing verifiable experience in required skill(s): {', '.join(missing_skills)}. "
            f"Recommended to probe practical knowledge or capacity to upskill during interview."
        )
    else:
        weaknesses = "No major gaps identified in required core technical competencies."

    explanation = (
        f"Candidate {cand_name} matches {int(skills_score)}% of technical skills required for {job_title}. "
        f"Experience rating stands at {int(experience_score)}% and education alignment at {int(education_score)}%. "
        f"{'Candidate is highly qualified with proven domain expertise.' if overall_score >= 85 else 'Candidate shows strong potential but has skill gaps that warrant technical review.'}"
    )

    return {
        "overall_score": overall_score,
        "skills_score": round(skills_score, 1),
        "experience_score": round(experience_score, 1),
        "education_score": round(education_score, 1),
        "project_score": round(project_score, 1),
        "preferred_skills_score": round(preferred_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "partial_skills": partial_skills,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "ai_explanation": explanation,
        "recommendation": recommendation
    }

