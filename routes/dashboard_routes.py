from flask import Blueprint, render_template, redirect, url_for, session
import database
from utils.security import login_required
from utils.helpers import safe_json_loads, get_recommendation_meta
from routes.report_routes import get_dashboard_statistics

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def root():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/dashboard')
@login_required
def index():
    stats = get_dashboard_statistics()

    # Recent Jobs
    recent_jobs = database.fetch_all("""
        SELECT j.*, COUNT(ja.id) as applicant_count
        FROM jobs j
        LEFT JOIN job_applications ja ON j.id = ja.job_id
        GROUP BY j.id
        ORDER BY j.created_at DESC
        LIMIT 5
    """)

    # Recent Candidates
    recent_candidates = database.fetch_all("""
        SELECT c.*, MAX(cm.overall_score) as top_score
        FROM candidates c
        LEFT JOIN candidate_matches cm ON c.id = cm.candidate_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT 5
    """)

    # Top Matching Candidates
    top_matches = database.fetch_all("""
        SELECT cm.*, c.name as candidate_name, c.email as candidate_email, c.recruitment_status,
               j.title as job_title, j.department
        FROM candidate_matches cm
        JOIN candidates c ON cm.candidate_id = c.id
        JOIN jobs j ON cm.job_id = j.id
        ORDER BY cm.overall_score DESC
        LIMIT 5
    """)
    for m in top_matches:
        m['rec_meta'] = get_recommendation_meta(m['overall_score'])

    # Recent Interviews
    recent_interviews = database.fetch_all("""
        SELECT i.*, c.name as candidate_name, j.title as job_title
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        JOIN jobs j ON i.job_id = j.id
        ORDER BY i.scheduled_date DESC, i.scheduled_time DESC
        LIMIT 5
    """)

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_jobs=recent_jobs,
        recent_candidates=recent_candidates,
        top_matches=top_matches,
        recent_interviews=recent_interviews
    )

