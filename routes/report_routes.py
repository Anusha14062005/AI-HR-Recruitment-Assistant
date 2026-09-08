import io
import csv
from flask import Blueprint, render_template, jsonify, Response
import database
from utils.security import login_required

report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports', methods=['GET'])
@login_required
def index():
    stats = get_dashboard_statistics()
    return render_template('reports.html', stats=stats)

@report_bp.route('/api/reports/dashboard', methods=['GET'])
@login_required
def api_dashboard_stats():
    stats = get_dashboard_statistics()
    return jsonify({'success': True, 'stats': stats})

@report_bp.route('/api/reports/export', methods=['GET'])
@login_required
def export_csv():
    """Export complete recruitment report as CSV."""
    rows = database.fetch_all("""
        SELECT c.id as candidate_id, c.name as candidate_name, c.email, c.location,
               c.years_experience, c.recruitment_status,
               j.title as applied_job, j.department,
               cm.overall_score as match_score, cm.recommendation as match_recommendation,
               ie.overall_score as interview_score, ie.final_recommendation as interview_recommendation
        FROM candidates c
        LEFT JOIN job_applications ja ON c.id = ja.candidate_id
        LEFT JOIN jobs j ON ja.job_id = j.id
        LEFT JOIN candidate_matches cm ON (cm.candidate_id = c.id AND cm.job_id = j.id)
        LEFT JOIN interviews i ON (i.candidate_id = c.id AND i.job_id = j.id)
        LEFT JOIN interview_evaluations ie ON i.id = ie.interview_id
        ORDER BY c.name ASC
    """)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Candidate ID', 'Candidate Name', 'Email', 'Location', 'Experience (Years)',
        'Recruitment Status', 'Applied Job', 'Department', 'AI Match Score (%)',
        'AI Recommendation', 'Interview Score (%)', 'Final Hiring Recommendation'
    ])

    for r in rows:
        writer.writerow([
            r.get('candidate_id'),
            r.get('candidate_name'),
            r.get('email'),
            r.get('location') or 'N/A',
            r.get('years_experience') or 0.0,
            r.get('recruitment_status'),
            r.get('applied_job') or 'General Pool',
            r.get('department') or 'N/A',
            r.get('match_score') or 'N/A',
            r.get('match_recommendation') or 'N/A',
            r.get('interview_score') or 'N/A',
            r.get('interview_recommendation') or 'N/A'
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=recruitment_report.csv"}
    )

def get_dashboard_statistics():
    """Aggregate statistics and chart datasets."""
    total_jobs = database.fetch_one("SELECT COUNT(*) as count FROM jobs")['count']
    active_jobs = database.fetch_one("SELECT COUNT(*) as count FROM jobs WHERE status = 'Active'")['count']
    total_candidates = database.fetch_one("SELECT COUNT(*) as count FROM candidates")['count']
    resumes_analyzed = database.fetch_one("SELECT COUNT(*) as count FROM resumes")['count']
    shortlisted_candidates = database.fetch_one("SELECT COUNT(*) as count FROM candidates WHERE recruitment_status = 'Shortlisted'")['count']
    interviews_completed = database.fetch_one("SELECT COUNT(*) as count FROM interviews WHERE status = 'Completed'")['count']
    selected_candidates = database.fetch_one("SELECT COUNT(*) as count FROM candidates WHERE recruitment_status = 'Selected'")['count']

    avg_score_row = database.fetch_one("SELECT AVG(overall_score) as avg_score FROM candidate_matches")
    avg_score = round(avg_score_row['avg_score'] or 0.0, 1)

    # 1. Status distribution
    status_counts = database.fetch_all("""
        SELECT recruitment_status, COUNT(*) as count 
        FROM candidates 
        GROUP BY recruitment_status
    """)
    status_labels = [s['recruitment_status'] for s in status_counts]
    status_values = [s['count'] for s in status_counts]

    # 2. Match score distribution
    score_buckets = database.fetch_all("""
        SELECT 
            SUM(CASE WHEN overall_score >= 85 THEN 1 ELSE 0 END) as bucket_strong,
            SUM(CASE WHEN overall_score >= 70 AND overall_score < 85 THEN 1 ELSE 0 END) as bucket_potential,
            SUM(CASE WHEN overall_score < 70 THEN 1 ELSE 0 END) as bucket_review
        FROM candidate_matches
    """)
    b = score_buckets[0] if score_buckets else {'bucket_strong': 0, 'bucket_potential': 0, 'bucket_review': 0}
    score_dist = {
        'labels': ['Strong Match (85-100%)', 'Potential Match (70-84%)', 'Needs Review (<70%)'],
        'values': [b.get('bucket_strong') or 0, b.get('bucket_potential') or 0, b.get('bucket_review') or 0]
    }

    # 3. Applicants per Job
    job_applicants = database.fetch_all("""
        SELECT j.title, COUNT(ja.id) as count
        FROM jobs j
        LEFT JOIN job_applications ja ON j.id = ja.job_id
        GROUP BY j.id
        ORDER BY count DESC
        LIMIT 6
    """)
    job_labels = [j['title'][:25] + ('...' if len(j['title']) > 25 else '') for j in job_applicants]
    job_values = [j['count'] for j in job_applicants]

    return {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_candidates': total_candidates,
        'resumes_analyzed': resumes_analyzed,
        'shortlisted_candidates': shortlisted_candidates,
        'interviews_completed': interviews_completed,
        'selected_candidates': selected_candidates,
        'avg_match_score': avg_score,
        'charts': {
            'status': {'labels': status_labels, 'values': status_values},
            'scores': score_dist,
            'job_applicants': {'labels': job_labels, 'values': job_values}
        }
    }

