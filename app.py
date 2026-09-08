import os
import logging
from flask import Flask, render_template, session, jsonify, request
from flask_cors import CORS
from config import Config
import database
from utils.helpers import get_status_badge, get_recommendation_meta, format_datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("App")

def create_app():
    """Application factory for AI HR Recruitment Assistant."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload directory exists
    Config.ensure_upload_dir()

    # Initialize database connection check
    database.init_db_connection()

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.job_routes import job_bp
    from routes.candidate_routes import candidate_bp
    from routes.resume_routes import resume_bp
    from routes.matching_routes import matching_bp
    from routes.interview_routes import interview_bp
    from routes.report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(report_bp)

    # Global Context Processors for Jinja templates
    @app.context_processor
    def inject_global_vars():
        current_user = None
        if session.get('user_id'):
            current_user = {
                'id': session.get('user_id'),
                'name': session.get('user_name', 'HR User'),
                'email': session.get('user_email', ''),
                'role': session.get('user_role', 'HR Manager'),
                'company': session.get('company', 'TalentFlow Global')
            }
        return {
            'current_user': current_user,
            'demo_mode': Config.DEMO_MODE,
            'ai_provider': Config.AI_PROVIDER,
            'db_mode': database.get_db_mode(),
            'get_status_badge': get_status_badge,
            'get_recommendation_meta': get_recommendation_meta,
            'format_datetime': format_datetime
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Endpoint not found.'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(413)
    def file_too_large(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Uploaded file exceeds 16MB limit.'}), 413
        return render_template('413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Internal server error occurred.'}), 500
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 65)
    print("   AI HR RECRUITMENT ASSISTANT - SERVER LAUNCHING")
    print("=" * 65)
    print(f"   * Environment:   {os.getenv('FLASK_ENV', 'development')}")
    print(f"   * Database:      Active mode [{database.get_db_mode().upper()}]")
    print(f"   * AI Engine:     Provider [{Config.AI_PROVIDER.upper()}] | DEMO_MODE [{Config.DEMO_MODE}]")
    print("   * Local URL:     http://127.0.0.1:5000")
    print("   * Default Login: admin@recruitment.ai | Admin@123")
    print("=" * 65 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=True)

