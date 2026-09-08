import json
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import database
from utils.security import login_required
from utils.helpers import safe_json_loads, get_recommendation_meta
from services.matching_service import compute_match

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/matching', methods=['GET', 'POST'])
@login_required
def matching_page():
    jobs = database.fetch_all("SELECT id, title, department FROM jobs WHERE status = 'Active' ORDER BY title")
    candidates = database.fetch_all("SELECT id, name, current_title, email FROM candidates ORDER BY name")

    selected_job_id = request.args.get('job_id', type=int) or (jobs[0]['id'] if jobs else None)
    selected_cand_id = request.args.get('candidate_id', type=int) or (candidates[0]['id'] if candidates else None)

    match_data = None
    job_details = None
    candidate_details = None

    if selected_job_id and selected_cand_id:
        job_details = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (selected_job_id,))
        job_skills = database.fetch_all("SELECT skill_name, is_required FROM job_skills WHERE job_id = %s", (selected_job_id,))
        if job_details:
            job_details['required_skills'] = [s['skill_name'] for s in job_skills if s['is_required']]
            job_details['preferred_skills'] = [s['skill_name'] for s in job_skills if not s['is_required']]

        candidate_details = database.fetch_one("SELECT * FROM candidates WHERE id = %s", (selected_cand_id,))
        if candidate_details:
            candidate_details['skills'] = database.fetch_all("SELECT skill_name, category, proficiency FROM candidate_skills WHERE candidate_id = %s", (selected_cand_id,))
            candidate_details['projects'] = database.fetch_all("SELECT project_title, description, technologies_used FROM candidate_projects WHERE candidate_id = %s", (selected_cand_id,))
            candidate_details['education'] = database.fetch_all("SELECT degree, institution FROM candidate_education WHERE candidate_id = %s", (selected_cand_id,))
            candidate_details['experience'] = database.fetch_all("SELECT company, title, description FROM candidate_experience WHERE candidate_id = %s", (selected_cand_id,))

        # Check existing match in database
        existing_match = database.fetch_one("""
            SELECT * FROM candidate_matches WHERE job_id = %s AND candidate_id = %s
        """, (selected_job_id, selected_cand_id))

        if existing_match:
            match_data = existing_match
            match_data['matched_skills'] = safe_json_loads(existing_match.get('matched_skills'))
            match_data['missing_skills'] = safe_json_loads(existing_match.get('missing_skills'))
            match_data['partial_skills'] = safe_json_loads(existing_match.get('partial_skills'))
            match_data['rec_meta'] = get_recommendation_meta(match_data['overall_score'])
        elif job_details and candidate_details:
            # Dynamically compute and store
            computed = compute_match(candidate_details, job_details)
            database.execute_query("""
                INSERT INTO candidate_matches 
                (job_id, candidate_id, overall_score, skills_score, experience_score, education_score, 
                 project_score, preferred_skills_score, matched_skills, missing_skills, partial_skills, 
                 strengths, weaknesses, ai_explanation, recommendation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                selected_job_id, selected_cand_id, computed['overall_score'], computed['skills_score'],
                computed['experience_score'], computed['education_score'], computed['project_score'],
                computed['preferred_skills_score'], json.dumps(computed['matched_skills']),
                json.dumps(computed['missing_skills']), json.dumps(computed['partial_skills']),
                computed['strengths'], computed['weaknesses'], computed['ai_explanation'], computed['recommendation']
            ))
            match_data = computed
            match_data['rec_meta'] = get_recommendation_meta(match_data['overall_score'])

    return render_template(
        'matching.html',
        jobs=jobs,
        candidates=candidates,
        selected_job_id=selected_job_id,
        selected_cand_id=selected_cand_id,
        job=job_details,
        candidate=candidate_details,
        match=match_data
    )

@matching_bp.route('/ranking', methods=['GET'])
@login_required
def ranking_page():
    jobs = database.fetch_all("SELECT id, title, department FROM jobs ORDER BY created_at DESC")
    selected_job_id = request.args.get('job_id', type=int) or (jobs[0]['id'] if jobs else None)
    
    ranked_candidates = []
    job_details = None

    if selected_job_id:
        job_details = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (selected_job_id,))
        
        # Get all candidates with their match scores for this job
        ranked_candidates = database.fetch_all("""
            SELECT c.id, c.name, c.email, c.location, c.current_title, c.years_experience, c.recruitment_status,
                   cm.overall_score, cm.skills_score, cm.experience_score, cm.missing_skills, cm.recommendation
            FROM candidates c
            LEFT JOIN candidate_matches cm ON (cm.candidate_id = c.id AND cm.job_id = %s)
            ORDER BY COALESCE(cm.overall_score, 0) DESC, c.years_experience DESC
        """, (selected_job_id,))

        for rank, c in enumerate(ranked_candidates, 1):
            c['rank'] = rank
            c['missing_skills_list'] = safe_json_loads(c.get('missing_skills'))
            score = c.get('overall_score') or 0.0
            c['rec_meta'] = get_recommendation_meta(score)

    return render_template(
        'ranking.html',
        jobs=jobs,
        selected_job_id=selected_job_id,
        job=job_details,
        candidates=ranked_candidates
    )

# ==================== JSON REST API ====================

@matching_bp.route('/api/jobs/<int:job_id>/matches', methods=['GET'])
def api_job_matches(job_id):
    matches = database.fetch_all("""
        SELECT cm.*, c.name as candidate_name, c.email as candidate_email, c.years_experience
        FROM candidate_matches cm
        JOIN candidates c ON cm.candidate_id = c.id
        WHERE cm.job_id = %s
        ORDER BY cm.overall_score DESC
    """, (job_id,))
    for m in matches:
        m['matched_skills'] = safe_json_loads(m.get('matched_skills'))
        m['missing_skills'] = safe_json_loads(m.get('missing_skills'))
        m['partial_skills'] = safe_json_loads(m.get('partial_skills'))
    return jsonify({'success': True, 'matches': matches})

@matching_bp.route('/api/jobs/<int:job_id>/match/<int:candidate_id>', methods=['POST'])
@login_required
def api_recompute_match(job_id, candidate_id):
    job = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (job_id,))
    if not job:
        return jsonify({'success': False, 'error': 'Job not found.'}), 404

    job_skills = database.fetch_all("SELECT skill_name, is_required FROM job_skills WHERE job_id = %s", (job_id,))
    job['required_skills'] = [s['skill_name'] for s in job_skills if s['is_required']]
    job['preferred_skills'] = [s['skill_name'] for s in job_skills if not s['is_required']]

    candidate = database.fetch_one("SELECT * FROM candidates WHERE id = %s", (candidate_id,))
    if not candidate:
        return jsonify({'success': False, 'error': 'Candidate not found.'}), 404

    candidate['skills'] = database.fetch_all("SELECT skill_name, category, proficiency FROM candidate_skills WHERE candidate_id = %s", (candidate_id,))
    candidate['projects'] = database.fetch_all("SELECT project_title, description, technologies_used FROM candidate_projects WHERE candidate_id = %s", (candidate_id,))
    candidate['education'] = database.fetch_all("SELECT degree, institution FROM candidate_education WHERE candidate_id = %s", (candidate_id,))
    candidate['experience'] = database.fetch_all("SELECT company, title, description FROM candidate_experience WHERE candidate_id = %s", (candidate_id,))

    computed = compute_match(candidate, job)

    database.execute_query("""
        INSERT INTO candidate_matches 
        (job_id, candidate_id, overall_score, skills_score, experience_score, education_score, 
         project_score, preferred_skills_score, matched_skills, missing_skills, partial_skills, 
         strengths, weaknesses, ai_explanation, recommendation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            overall_score = VALUES(overall_score),
            skills_score = VALUES(skills_score),
            experience_score = VALUES(experience_score),
            education_score = VALUES(education_score),
            project_score = VALUES(project_score),
            preferred_skills_score = VALUES(preferred_skills_score),
            matched_skills = VALUES(matched_skills),
            missing_skills = VALUES(missing_skills),
            partial_skills = VALUES(partial_skills),
            strengths = VALUES(strengths),
            weaknesses = VALUES(weaknesses),
            ai_explanation = VALUES(ai_explanation),
            recommendation = VALUES(recommendation)
    """, (
        job_id, candidate_id, computed['overall_score'], computed['skills_score'],
        computed['experience_score'], computed['education_score'], computed['project_score'],
        computed['preferred_skills_score'], json.dumps(computed['matched_skills']),
        json.dumps(computed['missing_skills']), json.dumps(computed['partial_skills']),
        computed['strengths'], computed['weaknesses'], computed['ai_explanation'], computed['recommendation']
    ))

    return jsonify({'success': True, 'match': computed})

