import json
from datetime import datetime, date
from flask import jsonify

def json_response(success=True, data=None, message="", status_code=200, **kwargs):
    """Standardized JSON response helper."""
    payload = {
        'success': success,
        'message': message,
        'data': data
    }
    payload.update(kwargs)
    return jsonify(payload), status_code

def safe_json_loads(data, default=None):
    """Safely decode JSON string or return default."""
    if default is None:
        default = []
    if data is None:
        return default
    if isinstance(data, (dict, list)):
        return data
    try:
        return json.loads(data)
    except Exception:
        return default

def get_recommendation_meta(score: float):
    """Return recommendation label and CSS badge based on score threshold."""
    try:
        score_val = float(score)
    except (ValueError, TypeError):
        score_val = 0.0
        
    if score_val >= 85.0:
        return {
            'label': 'Strong Match',
            'badge': 'badge-strong',
            'color': '#10b981',
            'action': 'Shortlist'
        }
    elif score_val >= 70.0:
        return {
            'label': 'Potential Match',
            'badge': 'badge-potential',
            'color': '#f59e0b',
            'action': 'Review'
        }
    else:
        return {
            'label': 'Needs Review',
            'badge': 'badge-needs-review',
            'color': '#ef4444',
            'action': 'Review'
        }

def get_status_badge(status: str):
    """Map recruitment status to bootstrap badge class."""
    status_map = {
        'New': 'bg-secondary',
        'Under Review': 'bg-info text-dark',
        'Shortlisted': 'bg-primary',
        'Interview Scheduled': 'bg-warning text-dark',
        'Selected': 'bg-success',
        'Rejected': 'bg-danger'
    }
    return status_map.get(status, 'bg-secondary')

def format_datetime(val):
    """Format datetime or string safely for display."""
    if not val:
        return "N/A"
    if isinstance(val, (datetime, date)):
        return val.strftime("%b %d, %Y")
    # If string
    try:
        dt = datetime.fromisoformat(str(val).replace("Z", ""))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(val)

