import os
import json
import logging
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import database
from config import Config
from utils.security import login_required, sanitize_filename
from utils.validators import validate_file_extension
from services.resume_parser import extract_text_from_file
from services.ai_service import AIService
from services.matching_service import compute_match

logger = logging.getLogger("ResumeRoutes")
resume_bp = Blueprint('resumes', __name__)

@resume_bp.route('/resume-analyzer', methods=['GET'])
@login_required
def analyzer_page():
    jobs = database.fetch_all("SELECT id, title, department FROM jobs WHERE status = 'Active' ORDER BY title")
    preselected_job = request.args.get('job_id', type=int)
    return render_template('resume_analyzer.html', jobs=jobs, preselected_job=preselected_job)

@resume_bp.route('/api/resumes/upload', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'success': False, 'error': 'No resume file uploaded.'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected.'}), 400

    if not validate_file_extension(file.filename, Config.ALLOWED_EXTENSIONS):
        return jsonify({'success': False, 'error': 'Unsupported file type. Please upload PDF or DOCX format.'}), 400

    # Ensure upload directory
    Config.ensure_upload_dir()

    # Save file with safe unique filename
    original_filename = secure_filename(file.filename) or "resume.pdf"
    stored_filename = sanitize_filename(original_filename)
    file_path = os.path.join(Config.UPLOAD_FOLDER, stored_filename)
    
    file.save(file_path)
    file_size = os.path.getsize(file_path)

    # 1. Extract text from file
    extracted_text = extract_text_from_file(file_path)
    if not extracted_text or len(extracted_text.strip()) < 20:
        logger.warning("Empty or unscannable resume uploaded.")
        extracted_text = f"Resume file: {original_filename}\nUnable to extract high-density text. Standard analysis applied."

    # 2. Parse entities using AI / local NLP
    parsed_data = AIService.analyze_resume_text(extracted_text)

    # 3. Create or update candidate record
    cand_name = parsed_data.get('name') or original_filename.rsplit('.', 1)[0].replace('_', ' ').title()
    cand_email = parsed_data.get('email') or f"candidate_{os.urandom(3).hex()}@example.com"
    cand_phone = parsed_data.get('phone', '')
    cand_loc = parsed_data.get('location', '')
    cand_title = parsed_data.get('current_title', 'Software Engineer')
    cand_exp = float(parsed_data.get('years_experience', 3.0))
    cand_summary = parsed_data.get('summary', '')

    existing_cand = database.fetch_one("SELECT id FROM candidates WHERE LOWER(email) = %s", (cand_email.lower(),))
    if existing_cand:
        candidate_id = existing_cand['id']
        database.execute_query("""
            UPDATE candidates 
            SET name = %s, phone = %s, location = %s, current_title = %s,
                years_experience = %s, ai_summary = %s
            WHERE id = %s
        """, (cand_name, cand_phone, cand_loc, cand_title, cand_exp, cand_summary, candidate_id))
    else:
        candidate_id = database.execute_insert("""
            INSERT INTO candidates (name, email, phone, location, current_title, years_experience, recruitment_status, ai_summary)
            VALUES (%s, %s, %s, %s, %s, %s, 'New', %s)
        """, (cand_name, cand_email, cand_phone, cand_loc, cand_title, cand_exp, cand_summary))

    # 4. Save resume record
    rel_path = os.path.relpath(file_path, Config.BASE_DIR).replace('\\', '/')
    database.execute_insert("""
        INSERT INTO resumes (candidate_id, filename, original_filename, file_path, file_size, file_type, extracted_text, raw_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (candidate_id, stored_filename, original_filename, rel_path, file_size, file.content_type or 'application/octet-stream', extracted_text, json.dumps(parsed_data)))

    # 5. Insert candidate skills
    database.execute_query("DELETE FROM candidate_skills WHERE candidate_id = %s", (candidate_id,))
    for s in parsed_data.get('skills', []):
        s_name = s.get('skill_name') if isinstance(s, dict) else str(s)
        s_cat = s.get('category', 'General') if isinstance(s, dict) else 'General'
        s_prof = s.get('proficiency', 'Intermediate') if isinstance(s, dict) else 'Intermediate'
        if s_name:
            database.execute_insert("""
                INSERT INTO candidate_skills (candidate_id, skill_name, category, proficiency)
                VALUES (%s, %s, %s, %s)
            """, (candidate_id, s_name, s_cat, s_prof))

    # 6. Insert education
    database.execute_query("DELETE FROM candidate_education WHERE candidate_id = %s", (candidate_id,))
    for edu in parsed_data.get('education', []):
        database.execute_insert("""
            INSERT INTO candidate_education (candidate_id, degree, institution, field_of_study, graduation_year, grade)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (candidate_id, edu.get('degree', 'Degree'), edu.get('institution', 'University'), edu.get('field_of_study', ''), str(edu.get('graduation_year', '')), edu.get('grade', '')))

    # 7. Insert experience
    database.execute_query("DELETE FROM candidate_experience WHERE candidate_id = %s", (candidate_id,))
    for exp in parsed_data.get('experience', []):
        database.execute_insert("""
            INSERT INTO candidate_experience (candidate_id, company, title, start_date, end_date, is_current, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (candidate_id, exp.get('company', 'Company'), exp.get('title', 'Role'), exp.get('start_date', ''), exp.get('end_date', ''), 1 if exp.get('is_current') else 0, exp.get('description', '')))

    # 8. Insert projects
    database.execute_query("DELETE FROM candidate_projects WHERE candidate_id = %s", (candidate_id,))
    for proj in parsed_data.get('projects', []):
        database.execute_insert("""
            INSERT INTO candidate_projects (candidate_id, project_title, description, technologies_used)
            VALUES (%s, %s, %s, %s)
        """, (candidate_id, proj.get('project_title', 'Project'), proj.get('description', ''), proj.get('technologies_used', '')))

    # 9. If job_id provided, link application and compute match score
    job_id = request.form.get('job_id', type=int)
    match_result = None
    if job_id:
        # Create application record
        database.execute_query("""
            INSERT INTO job_applications (job_id, candidate_id, status)
            VALUES (%s, %s, 'Applied')
            ON DUPLICATE KEY UPDATE status = VALUES(status)
        """, (job_id, candidate_id))

        # Retrieve job details & skills
        job = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (job_id,))
        job_skills = database.fetch_all("SELECT skill_name, is_required FROM job_skills WHERE job_id = %s", (job_id,))
        job['required_skills'] = [s['skill_name'] for s in job_skills if s['is_required']]
        job['preferred_skills'] = [s['skill_name'] for s in job_skills if not s['is_required']]
        job['experience_required_years'] = 3.0

        # Run 5-factor matching
        parsed_data['extracted_text'] = extracted_text
        match_result = compute_match(parsed_data, job)

        # Store in candidate_matches
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
            job_id, candidate_id, match_result['overall_score'], match_result['skills_score'],
            match_result['experience_score'], match_result['education_score'], match_result['project_score'],
            match_result['preferred_skills_score'], json.dumps(match_result['matched_skills']),
            json.dumps(match_result['missing_skills']), json.dumps(match_result['partial_skills']),
            match_result['strengths'], match_result['weaknesses'], match_result['ai_explanation'],
            match_result['recommendation']
        ))

    return jsonify({
        'success': True,
        'message': f"Resume for '{cand_name}' processed and analyzed successfully!",
        'candidate_id': candidate_id,
        'parsed_data': parsed_data,
        'match_result': match_result
    }), 201

@resume_bp.route('/api/resumes/<int:resume_id>', methods=['GET'])
@login_required
def api_get_resume(resume_id):
    resume = database.fetch_one("SELECT * FROM resumes WHERE id = %s", (resume_id,))
    if not resume:
        return jsonify({'success': False, 'error': 'Resume not found.'}), 404
    return jsonify({'success': True, 'resume': resume})

@resume_bp.route('/api/ai/analyze-resume', methods=['POST'])
@login_required
def api_analyze_resume_text():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    if not text:
        return jsonify({'success': False, 'error': 'Text is required.'}), 400
    parsed = AIService.analyze_resume_text(text)
    return jsonify({'success': True, 'parsed': parsed})

