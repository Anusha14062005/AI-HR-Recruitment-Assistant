from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import database
from utils.security import login_required
from utils.helpers import safe_json_loads, get_recommendation_meta

candidate_bp = Blueprint('candidates', __name__)

@candidate_bp.route('/candidates', methods=['GET'])
@login_required
def index():
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    sort_by = request.args.get('sort', 'newest')

    sql = """
        SELECT c.*, 
               COUNT(DISTINCT ja.job_id) as applied_jobs_count,
               MAX(cm.overall_score) as top_match_score,
               GROUP_CONCAT(DISTINCT cs.skill_name) as skills_list
        FROM candidates c
        LEFT JOIN job_applications ja ON c.id = ja.candidate_id
        LEFT JOIN candidate_matches cm ON c.id = cm.candidate_id
        LEFT JOIN candidate_skills cs ON c.id = cs.candidate_id
        WHERE 1=1
    """
    params = []

    if search:
        sql += " AND (c.name LIKE %s OR c.email LIKE %s OR c.location LIKE %s OR cs.skill_name LIKE %s)"
        like = f"%{search}%"
        params.extend([like, like, like, like])

    if status_filter:
        sql += " AND c.recruitment_status = %s"
        params.append(status_filter)

    sql += " GROUP BY c.id"

    # Sorting
    if sort_by == 'score':
        sql += " ORDER BY top_match_score DESC"
    elif sort_by == 'exp':
        sql += " ORDER BY c.years_experience DESC"
    elif sort_by == 'name':
        sql += " ORDER BY c.name ASC"
    else:
        sql += " ORDER BY c.created_at DESC"

    candidates = database.fetch_all(sql, params)

    return render_template(
        'candidates.html',
        candidates=candidates,
        selected_status=status_filter,
        search_query=search,
        selected_sort=sort_by
    )

@candidate_bp.route('/candidates/<int:candidate_id>', methods=['GET'])
@login_required
def candidate_profile(candidate_id):
    candidate = database.fetch_one("SELECT * FROM candidates WHERE id = %s", (candidate_id,))
    if not candidate:
        flash('Candidate not found.', 'warning')
        return redirect(url_for('candidates.index'))

    # Profile components
    skills = database.fetch_all("SELECT * FROM candidate_skills WHERE candidate_id = %s ORDER BY category, skill_name", (candidate_id,))
    education = database.fetch_all("SELECT * FROM candidate_education WHERE candidate_id = %s ORDER BY graduation_year DESC", (candidate_id,))
    experience = database.fetch_all("SELECT * FROM candidate_experience WHERE candidate_id = %s ORDER BY start_date DESC", (candidate_id,))
    projects = database.fetch_all("SELECT * FROM candidate_projects WHERE candidate_id = %s", (candidate_id,))
    certifications = database.fetch_all("SELECT * FROM candidate_certifications WHERE candidate_id = %s", (candidate_id,))
    resumes = database.fetch_all("SELECT * FROM resumes WHERE candidate_id = %s ORDER BY uploaded_at DESC", (candidate_id,))

    # Applied jobs & Matches
    matches = database.fetch_all("""
        SELECT cm.*, j.title as job_title, j.department, j.location as job_location
        FROM candidate_matches cm
        JOIN jobs j ON cm.job_id = j.id
        WHERE cm.candidate_id = %s
        ORDER BY cm.overall_score DESC
    """, (candidate_id,))

    # Parse JSON fields in matches
    for m in matches:
        m['matched_skills_list'] = safe_json_loads(m.get('matched_skills'))
        m['missing_skills_list'] = safe_json_loads(m.get('missing_skills'))
        m['partial_skills_list'] = safe_json_loads(m.get('partial_skills'))
        m['rec_meta'] = get_recommendation_meta(m['overall_score'])

    # Interviews and evaluations
    interviews = database.fetch_all("""
        SELECT i.*, j.title as job_title,
               ie.overall_score as eval_score, ie.final_recommendation, ie.strengths, ie.weaknesses
        FROM interviews i
        JOIN jobs j ON i.job_id = j.id
        LEFT JOIN interview_evaluations ie ON i.id = ie.interview_id
        WHERE i.candidate_id = %s
        ORDER BY i.scheduled_date DESC, i.scheduled_time DESC
    """, (candidate_id,))

    # Active jobs for quick-match modal
    all_jobs = database.fetch_all("SELECT id, title, department FROM jobs WHERE status = 'Active' ORDER BY title")

    return render_template(
        'candidate_details.html',
        candidate=candidate,
        skills=skills,
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
        resumes=resumes,
        matches=matches,
        interviews=interviews,
        all_jobs=all_jobs
    )

@candidate_bp.route('/candidates/<int:candidate_id>/status', methods=['POST'])
@login_required
def update_status(candidate_id):
    new_status = request.form.get('status')
    valid_statuses = ['New', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
    if new_status in valid_statuses:
        database.execute_query("UPDATE candidates SET recruitment_status = %s WHERE id = %s", (new_status, candidate_id))
        flash(f"Candidate recruitment status updated to '{new_status}'.", 'success')
    else:
        flash("Invalid status specified.", 'danger')
    return redirect(url_for('candidates.candidate_profile', candidate_id=candidate_id))

# ==================== JSON REST API ====================

@candidate_bp.route('/api/candidates', methods=['GET'])
def api_get_candidates():
    candidates = database.fetch_all("SELECT * FROM candidates ORDER BY created_at DESC")
    return jsonify({'success': True, 'candidates': candidates})

@candidate_bp.route('/api/candidates/<int:candidate_id>', methods=['GET'])
def api_get_candidate(candidate_id):
    candidate = database.fetch_one("SELECT * FROM candidates WHERE id = %s", (candidate_id,))
    if not candidate:
        return jsonify({'success': False, 'error': 'Candidate not found.'}), 404
    skills = database.fetch_all("SELECT * FROM candidate_skills WHERE candidate_id = %s", (candidate_id,))
    education = database.fetch_all("SELECT * FROM candidate_education WHERE candidate_id = %s", (candidate_id,))
    experience = database.fetch_all("SELECT * FROM candidate_experience WHERE candidate_id = %s", (candidate_id,))
    projects = database.fetch_all("SELECT * FROM candidate_projects WHERE candidate_id = %s", (candidate_id,))
    candidate['skills'] = skills
    candidate['education'] = education
    candidate['experience'] = experience
    candidate['projects'] = projects
    return jsonify({'success': True, 'candidate': candidate})

@candidate_bp.route('/api/candidates/<int:candidate_id>/status', methods=['PUT'])
@login_required
def api_update_status(candidate_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get('status')
    valid_statuses = ['New', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'error': 'Invalid status.'}), 400

    database.execute_query("UPDATE candidates SET recruitment_status = %s WHERE id = %s", (new_status, candidate_id))
    return jsonify({'success': True, 'message': 'Status updated successfully.', 'status': new_status})

