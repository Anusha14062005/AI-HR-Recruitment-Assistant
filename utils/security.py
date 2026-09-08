import os
import re
import uuid
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hash password using Werkzeug's default robust method (scrypt/pbkdf2)."""
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    """Safely verify raw password against stored hash."""
    if not password_hash or not password:
        return False
    return check_password_hash(password_hash, password)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and inject a unique ID."""
    name, ext = os.path.splitext(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:50]
    unique_suffix = uuid.uuid4().hex[:8]
    clean_ext = ext.lower()
    return f"{clean_name}_{unique_suffix}{clean_ext}"

def login_required(f):
    """Decorator to enforce HR authentication on routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            # If it's an API request, return 401 JSON
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Authentication required. Please log in.'
                }), 401
            # Otherwise redirect to login page with next param
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

