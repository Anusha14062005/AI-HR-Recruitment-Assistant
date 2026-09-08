from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import database
from utils.security import login_required
from services.ai_service import AIService
from services.job_analyzer import parse_job_description_offline

job_bp = Blueprint('jobs', __name__)

@job_bp.route('/jobs', methods=['GET'])
@login_required
def index():
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    dept_filter = request.args.get('dept', '').strip()

    sql = """
        SELECT j.*, u.name as created_by_name,
               COUNT(ja.id) as applicant_count
        FROM jobs j
        LEFT JOIN users u ON j.user_id = u.id
        LEFT JOIN job_applications ja ON j.id = ja.job_id
        WHERE 1=1
    """
    params = []

    if search_query:
        sql += " AND (j.title LIKE %s OR j.description LIKE %s OR j.location LIKE %s)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term])

    if status_filter:
        sql += " AND j.status = %s"
        params.append(status_filter)

    if dept_filter:
        sql += " AND j.department = %s"
        params.append(dept_filter)

    sql += " GROUP BY j.id ORDER BY j.created_at DESC"
    jobs = database.fetch_all(sql, params)

    # Get distinct departments for filter dropdown
    depts = database.fetch_all("SELECT DISTINCT department FROM jobs WHERE department IS NOT NULL ORDER BY department")

    return render_template(
        'jobs.html',
        jobs=jobs,
        departments=[d['department'] for d in depts],
        selected_dept=dept_filter,
        selected_status=status_filter,
        search_query=search_query
    )

@job_bp.route('/jobs/create', methods=['GET', 'POST'])
@login_required
def create_job():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', '').strip()
        employment_type = request.form.get('employment_type', 'Full Time')
        experience_required = request.form.get('experience_required', '3+ Years').strip()
        min_salary = request.form.get('min_salary', None)
        max_salary = request.form.get('max_salary', None)
        description = request.form.get('description', '').strip()
        education_requirements = request.form.get('education_requirements', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        status = request.form.get('status', 'Active')

        raw_req_skills = request.form.get('required_skills', '')
        raw_pref_skills = request.form.get('preferred_skills', '')

        if not title or not department or not description:
            flash('Job Title, Department, and Description are required fields.', 'danger')
            return render_template('create_job.html')

        # Clean salary values
        min_sal = float(min_salary) if min_salary and min_salary.strip() else None
        max_sal = float(max_salary) if max_salary and max_salary.strip() else None

        job_id = database.execute_insert(
            """INSERT INTO jobs 
               (user_id, title, department, location, employment_type, experience_required, 
                min_salary, max_salary, description, education_requirements, responsibilities, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (session['user_id'], title, department, location, employment_type, experience_required,
             min_sal, max_sal, description, education_requirements, responsibilities, status)
        )

        # Parse skills
        req_skills = [s.strip() for s in raw_req_skills.split(',') if s.strip()]
        pref_skills = [s.strip() for s in raw_pref_skills.split(',') if s.strip()]

        # If no skills entered manually, use AI/offline JD analyzer
        if not req_skills and not pref_skills:
            analysis = AIService.analyze_job_description(title, description, responsibilities)
            req_skills = analysis.get('required_skills', [])
            pref_skills = analysis.get('preferred_skills', [])

        for s in req_skills:
            database.execute_insert(
                "INSERT INTO job_skills (job_id, skill_name, is_required, category) VALUES (%s, %s, %s, %s)",
                (job_id, s, True, 'Required')
            )
        for s in pref_skills:
            database.execute_insert(
                "INSERT INTO job_skills (job_id, skill_name, is_required, category) VALUES (%s, %s, %s, %s)",
                (job_id, s, False, 'Preferred')
            )

        flash(f"Job '{title}' created successfully with {len(req_skills) + len(pref_skills)} extracted skills.", 'success')
        return redirect(url_for('jobs.view_job', job_id=job_id))

    return render_template('create_job.html')

@job_bp.route('/jobs/<int:job_id>', methods=['GET'])
@login_required
def view_job(job_id):
    job = database.fetch_one("""
        SELECT j.*, u.name as created_by_name, u.email as created_by_email
        FROM jobs j
        LEFT JOIN users u ON j.user_id = u.id
        WHERE j.id = %s
    """, (job_id,))

    if not job:
        flash('Job not found.', 'warning')
        return redirect(url_for('jobs.index'))

    skills = database.fetch_all("SELECT * FROM job_skills WHERE job_id = %s ORDER BY is_required DESC, skill_name ASC", (job_id,))
    required_skills = [s for s in skills if s['is_required']]
    preferred_skills = [s for s in skills if not s['is_required']]

    # Fetch applicants with their match scores
    applicants = database.fetch_all("""
        SELECT c.*, ja.applied_at, ja.status as application_status,
               cm.overall_score, cm.recommendation
        FROM job_applications ja
        JOIN candidates c ON ja.candidate_id = c.id
        LEFT JOIN candidate_matches cm ON (cm.job_id = ja.job_id AND cm.candidate_id = c.id)
        WHERE ja.job_id = %s
        ORDER BY cm.overall_score DESC, ja.applied_at DESC
    """, (job_id,))

    return render_template(
        'job_details.html',
        job=job,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        applicants=applicants
    )

@job_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (job_id,))
    if not job:
        flash('Job not found.', 'warning')
        return redirect(url_for('jobs.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', '').strip()
        employment_type = request.form.get('employment_type', 'Full Time')
        experience_required = request.form.get('experience_required', '3+ Years').strip()
        min_salary = request.form.get('min_salary', None)
        max_salary = request.form.get('max_salary', None)
        description = request.form.get('description', '').strip()
        education_requirements = request.form.get('education_requirements', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        status = request.form.get('status', 'Active')

        raw_req_skills = request.form.get('required_skills', '')
        raw_pref_skills = request.form.get('preferred_skills', '')

        min_sal = float(min_salary) if min_salary and min_salary.strip() else None
        max_sal = float(max_salary) if max_salary and max_salary.strip() else None

        database.execute_query("""
            UPDATE jobs 
            SET title = %s, department = %s, location = %s, employment_type = %s,
                experience_required = %s, min_salary = %s, max_salary = %s,
                description = %s, education_requirements = %s, responsibilities = %s, status = %s
            WHERE id = %s
        """, (title, department, location, employment_type, experience_required,
              min_sal, max_sal, description, education_requirements, responsibilities, status, job_id))

        # Update skills
        database.execute_query("DELETE FROM job_skills WHERE job_id = %s", (job_id,))
        for s in [s.strip() for s in raw_req_skills.split(',') if s.strip()]:
            database.execute_insert("INSERT INTO job_skills (job_id, skill_name, is_required, category) VALUES (%s, %s, %s, %s)", (job_id, s, True, 'Required'))
        for s in [s.strip() for s in raw_pref_skills.split(',') if s.strip()]:
            database.execute_insert("INSERT INTO job_skills (job_id, skill_name, is_required, category) VALUES (%s, %s, %s, %s)", (job_id, s, False, 'Preferred'))

        flash('Job details updated successfully.', 'success')
        return redirect(url_for('jobs.view_job', job_id=job_id))

    skills = database.fetch_all("SELECT * FROM job_skills WHERE job_id = %s", (job_id,))
    req_skills_str = ", ".join([s['skill_name'] for s in skills if s['is_required']])
    pref_skills_str = ", ".join([s['skill_name'] for s in skills if not s['is_required']])

    return render_template('edit_job.html', job=job, req_skills=req_skills_str, pref_skills=pref_skills_str)

@job_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    database.execute_query("DELETE FROM jobs WHERE id = %s", (job_id,))
    flash('Job deleted successfully.', 'info')
    return redirect(url_for('jobs.index'))

# ==================== JSON REST API ====================

@job_bp.route('/api/jobs', methods=['GET'])
def api_get_jobs():
    jobs = database.fetch_all("""
        SELECT j.*, COUNT(ja.id) as applicant_count 
        FROM jobs j 
        LEFT JOIN job_applications ja ON j.id = ja.job_id 
        GROUP BY j.id 
        ORDER BY j.created_at DESC
    """)
    return jsonify({'success': True, 'jobs': jobs})

@job_bp.route('/api/jobs', methods=['POST'])
@login_required
def api_create_job():
    data = request.get_json(silent=True) or {}
    title = data.get('title', '').strip()
    department = data.get('department', '').strip()
    location = data.get('location', '').strip()
    employment_type = data.get('employment_type', 'Full Time')
    experience_required = data.get('experience_required', '3+ Years')
    description = data.get('description', '').strip()

    if not title or not department or not description:
        return jsonify({'success': False, 'error': 'Missing required fields.'}), 400

    job_id = database.execute_insert("""
        INSERT INTO jobs (user_id, title, department, location, employment_type, experience_required, description, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
    """, (session['user_id'], title, department, location, employment_type, experience_required, description))

    # Auto analyze and save skills
    skills = data.get('skills', [])
    if not skills:
        analysis = AIService.analyze_job_description(title, description)
        for s in analysis.get('required_skills', []):
            database.execute_insert("INSERT INTO job_skills (job_id, skill_name, is_required) VALUES (%s, %s, %s)", (job_id, s, True))
        for s in analysis.get('preferred_skills', []):
            database.execute_insert("INSERT INTO job_skills (job_id, skill_name, is_required) VALUES (%s, %s, %s)", (job_id, s, False))

    return jsonify({'success': True, 'job_id': job_id, 'message': 'Job created successfully.'}), 201

@job_bp.route('/api/jobs/<int:job_id>', methods=['GET'])
def api_get_job(job_id):
    job = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (job_id,))
    if not job:
        return jsonify({'success': False, 'error': 'Job not found.'}), 404
    skills = database.fetch_all("SELECT * FROM job_skills WHERE job_id = %s", (job_id,))
    job['skills'] = skills
    return jsonify({'success': True, 'job': job})

@job_bp.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def api_delete_job(job_id):
    database.execute_query("DELETE FROM jobs WHERE id = %s", (job_id,))
    return jsonify({'success': True, 'message': 'Job deleted successfully.'})

@job_bp.route('/api/ai/analyze-job', methods=['POST'])
@login_required
def api_ai_analyze_job():
    data = request.get_json(silent=True) or {}
    title = data.get('title', '')
    description = data.get('description', '')
    responsibilities = data.get('responsibilities', '')

    if not description:
        return jsonify({'success': False, 'error': 'Job description text is required.'}), 400

    analysis = AIService.analyze_job_description(title, description, responsibilities)
    return jsonify({'success': True, 'analysis': analysis})

