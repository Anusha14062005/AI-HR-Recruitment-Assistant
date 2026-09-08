from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
import database
from utils.security import login_required
from services.interview_service import InterviewService

interview_bp = Blueprint('interviews', __name__)

@interview_bp.route('/interview-questions', methods=['GET', 'POST'])
@login_required
def questions_page():
    jobs = database.fetch_all("SELECT id, title FROM jobs WHERE status = 'Active' ORDER BY title")
    candidates = database.fetch_all("SELECT id, name, current_title FROM candidates ORDER BY name")

    selected_job_id = request.args.get('job_id', type=int) or (jobs[0]['id'] if jobs else None)
    selected_cand_id = request.args.get('candidate_id', type=int) or (candidates[0]['id'] if candidates else None)
    count = request.args.get('count', type=int, default=5)

    questions = []
    job_details = None
    candidate_details = None

    if selected_job_id and selected_cand_id:
        job_details = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (selected_job_id,))
        candidate_details = database.fetch_one("SELECT * FROM candidates WHERE id = %s", (selected_cand_id,))
        
        # Load existing saved questions from DB first
        saved_questions = database.fetch_all("""
            SELECT * FROM interview_questions 
            WHERE job_id = %s AND candidate_id = %s 
            ORDER BY id ASC
        """, (selected_job_id, selected_cand_id))

        if saved_questions and request.args.get('regenerate') != 'true':
            questions = saved_questions
        else:
            # Generate personalized questions using InterviewService
            if candidate_details and job_details:
                candidate_details['skills'] = database.fetch_all("SELECT skill_name FROM candidate_skills WHERE candidate_id = %s", (selected_cand_id,))
                candidate_details['projects'] = database.fetch_all("SELECT project_title, description FROM candidate_projects WHERE candidate_id = %s", (selected_cand_id,))
                
                # Check for missing skills
                match_rec = database.fetch_one("SELECT missing_skills FROM candidate_matches WHERE job_id = %s AND candidate_id = %s", (selected_job_id, selected_cand_id))
                if match_rec and match_rec.get('missing_skills'):
                    from utils.helpers import safe_json_loads
                    candidate_details['missing_skills'] = safe_json_loads(match_rec['missing_skills'])

                generated = InterviewService.generate_questions(candidate_details, job_details, count)
                
                # Save into database
                database.execute_query("DELETE FROM interview_questions WHERE job_id = %s AND candidate_id = %s", (selected_job_id, selected_cand_id))
                for q in generated:
                    database.execute_insert("""
                        INSERT INTO interview_questions (job_id, candidate_id, category, difficulty, question_text, expected_skills)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (selected_job_id, selected_cand_id, q.get('category', 'Technical'), q.get('difficulty', 'Medium'), q.get('question_text'), q.get('expected_skills', '')))

                questions = database.fetch_all("SELECT * FROM interview_questions WHERE job_id = %s AND candidate_id = %s", (selected_job_id, selected_cand_id))

    return render_template(
        'interview_questions.html',
        jobs=jobs,
        candidates=candidates,
        selected_job_id=selected_job_id,
        selected_cand_id=selected_cand_id,
        job=job_details,
        candidate=candidate_details,
        questions=questions,
        selected_count=count
    )

@interview_bp.route('/interview-questions/export', methods=['GET'])
@login_required
def export_questions():
    job_id = request.args.get('job_id', type=int)
    candidate_id = request.args.get('candidate_id', type=int)
    if not job_id or not candidate_id:
        flash("Please select both a job and a candidate to export questions.", "warning")
        return redirect(url_for('interviews.questions_page'))

    job = database.fetch_one("SELECT title FROM jobs WHERE id = %s", (job_id,))
    cand = database.fetch_one("SELECT name FROM candidates WHERE id = %s", (candidate_id,))
    questions = database.fetch_all("SELECT * FROM interview_questions WHERE job_id = %s AND candidate_id = %s", (job_id, candidate_id))

    content = InterviewService.export_questions_text(
        questions,
        cand['name'] if cand else "Candidate",
        job['title'] if job else "Position"
    )

    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename=interview_questions_{candidate_id}.txt"}
    )

@interview_bp.route('/interviews', methods=['GET', 'POST'])
@login_required
def interviews_list():
    if request.method == 'POST':
        candidate_id = request.form.get('candidate_id', type=int)
        job_id = request.form.get('job_id', type=int)
        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        interview_type = request.form.get('interview_type', 'Technical')
        interviewer_name = request.form.get('interviewer_name', '').strip()
        notes = request.form.get('notes', '').strip()

        if not candidate_id or not job_id or not scheduled_date or not scheduled_time or not interviewer_name:
            flash('All scheduling fields are required.', 'danger')
            return redirect(url_for('interviews.interviews_list'))

        interview_id = database.execute_insert("""
            INSERT INTO interviews (candidate_id, job_id, scheduled_date, scheduled_time, interview_type, interviewer_name, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled', %s)
        """, (candidate_id, job_id, scheduled_date, scheduled_time, interview_type, interviewer_name, notes))

        # Update candidate status
        database.execute_query("UPDATE candidates SET recruitment_status = 'Interview Scheduled' WHERE id = %s", (candidate_id,))

        flash('Interview scheduled successfully!', 'success')
        return redirect(url_for('interviews.interviews_list'))

    # List interviews
    interviews = database.fetch_all("""
        SELECT i.*, c.name as candidate_name, c.email as candidate_email,
               j.title as job_title, j.department,
               ie.overall_score, ie.final_recommendation
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        JOIN jobs j ON i.job_id = j.id
        LEFT JOIN interview_evaluations ie ON i.id = ie.interview_id
        ORDER BY i.scheduled_date DESC, i.scheduled_time DESC
    """)

    jobs = database.fetch_all("SELECT id, title FROM jobs WHERE status = 'Active' ORDER BY title")
    candidates = database.fetch_all("SELECT id, name FROM candidates ORDER BY name")

    return render_template('interviews.html', interviews=interviews, jobs=jobs, candidates=candidates)

@interview_bp.route('/interviews/<int:interview_id>/status', methods=['POST'])
@login_required
def update_interview_status(interview_id):
    status = request.form.get('status')
    if status in ['Scheduled', 'Completed', 'Cancelled']:
        database.execute_query("UPDATE interviews SET status = %s WHERE id = %s", (status, interview_id))
        flash(f"Interview marked as '{status}'.", 'success')
    return redirect(url_for('interviews.interviews_list'))

@interview_bp.route('/interviews/<int:interview_id>/evaluation', methods=['GET', 'POST'])
@login_required
def interview_evaluation(interview_id):
    interview = database.fetch_one("""
        SELECT i.*, c.name as candidate_name, c.email as candidate_email, c.recruitment_status,
               j.title as job_title, j.department
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        JOIN jobs j ON i.job_id = j.id
        WHERE i.id = %s
    """, (interview_id,))

    if not interview:
        flash('Interview not found.', 'warning')
        return redirect(url_for('interviews.interviews_list'))

    evaluation = database.fetch_one("SELECT * FROM interview_evaluations WHERE interview_id = %s", (interview_id,))

    if request.method == 'POST':
        tech = int(request.form.get('technical_score', 3))
        comm = int(request.form.get('communication_score', 3))
        prob = int(request.form.get('problem_solving_score', 3))
        proj = int(request.form.get('project_knowledge_score', 3))
        fit = int(request.form.get('role_fit_score', 3))
        conf = int(request.form.get('confidence_score', 3))
        strengths = request.form.get('strengths', '').strip()
        weaknesses = request.form.get('weaknesses', '').strip()
        notes = request.form.get('notes', '').strip()
        final_rec = request.form.get('final_recommendation', 'Consider')

        # Calculate overall score percentage (each factor 1-5, max total = 30)
        total_pts = tech + comm + prob + proj + fit + conf
        overall_score = round((total_pts / 30.0) * 100.0, 1)

        database.execute_query("""
            INSERT INTO interview_evaluations 
            (interview_id, candidate_id, job_id, technical_score, communication_score, problem_solving_score,
             project_knowledge_score, role_fit_score, confidence_score, overall_score, strengths, weaknesses, notes, final_recommendation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                technical_score = VALUES(technical_score),
                communication_score = VALUES(communication_score),
                problem_solving_score = VALUES(problem_solving_score),
                project_knowledge_score = VALUES(project_knowledge_score),
                role_fit_score = VALUES(role_fit_score),
                confidence_score = VALUES(confidence_score),
                overall_score = VALUES(overall_score),
                strengths = VALUES(strengths),
                weaknesses = VALUES(weaknesses),
                notes = VALUES(notes),
                final_recommendation = VALUES(final_recommendation)
        """, (interview_id, interview['candidate_id'], interview['job_id'], tech, comm, prob, proj, fit, conf,
              overall_score, strengths, weaknesses, notes, final_rec))

        # Mark interview completed
        database.execute_query("UPDATE interviews SET status = 'Completed' WHERE id = %s", (interview_id,))

        # Update candidate status based on evaluation
        if final_rec == 'Strongly Recommend':
            database.execute_query("UPDATE candidates SET recruitment_status = 'Selected' WHERE id = %s", (interview['candidate_id'],))
        elif final_rec == 'Not Recommended':
            database.execute_query("UPDATE candidates SET recruitment_status = 'Rejected' WHERE id = %s", (interview['candidate_id'],))

        flash('Interview evaluation submitted and candidate status updated!', 'success')
        return redirect(url_for('candidates.candidate_profile', candidate_id=interview['candidate_id']))

    return render_template('evaluation.html', interview=interview, evaluation=evaluation)

# ==================== JSON REST API ====================

@interview_bp.route('/api/interviews', methods=['GET'])
def api_get_interviews():
    interviews = database.fetch_all("SELECT * FROM interviews ORDER BY scheduled_date DESC")
    return jsonify({'success': True, 'interviews': interviews})

@interview_bp.route('/api/interviews', methods=['POST'])
@login_required
def api_create_interview():
    data = request.get_json(silent=True) or {}
    cand_id = data.get('candidate_id')
    job_id = data.get('job_id')
    date_val = data.get('scheduled_date')
    time_val = data.get('scheduled_time')
    interviewer = data.get('interviewer_name', 'HR Team')

    if not cand_id or not job_id or not date_val or not time_val:
        return jsonify({'success': False, 'error': 'Missing required interview fields.'}), 400

    iid = database.execute_insert("""
        INSERT INTO interviews (candidate_id, job_id, scheduled_date, scheduled_time, interview_type, interviewer_name, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
    """, (cand_id, job_id, date_val, time_val, data.get('interview_type', 'Technical'), interviewer))

    return jsonify({'success': True, 'interview_id': iid, 'message': 'Interview scheduled.'}), 201

@interview_bp.route('/api/ai/generate-interview-questions', methods=['POST'])
@login_required
def api_generate_questions():
    data = request.get_json(silent=True) or {}
    job_id = data.get('job_id')
    candidate_id = data.get('candidate_id')
    count = data.get('count', 5)

    job = database.fetch_one("SELECT * FROM jobs WHERE id = %s", (job_id,))
    cand = database.fetch_one("SELECT * FROM candidates WHERE id = %s", (candidate_id,))

    if not job or not cand:
        return jsonify({'success': False, 'error': 'Job or Candidate not found.'}), 404

    cand['skills'] = database.fetch_all("SELECT skill_name FROM candidate_skills WHERE candidate_id = %s", (candidate_id,))
    cand['projects'] = database.fetch_all("SELECT project_title, description FROM candidate_projects WHERE candidate_id = %s", (candidate_id,))

    questions = InterviewService.generate_questions(cand, job, count)
    return jsonify({'success': True, 'questions': questions})

