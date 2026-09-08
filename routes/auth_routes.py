from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import database
from utils.security import hash_password, verify_password, login_required
from utils.validators import validate_registration, validate_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html', email=email)

        user = database.fetch_one("SELECT * FROM users WHERE LOWER(email) = %s", (email,))
        if not user or not verify_password(user['password_hash'], password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

        # Establish session
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user.get('role', 'HR Manager')
        session['company'] = user.get('company', 'Acme Corp')

        flash(f"Welcome back, {user['name']}!", 'success')
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        company = request.form.get('company', '').strip() or 'Acme Corp'
        role = request.form.get('role', '').strip() or 'HR Manager'
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        is_valid, err = validate_registration(name, email, password, confirm_password)
        if not is_valid:
            flash(err, 'danger')
            return render_template('register.html', name=name, email=email, company=company, role=role)

        # Check existing email
        existing = database.fetch_one("SELECT id FROM users WHERE LOWER(email) = %s", (email,))
        if existing:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Insert user
        pwd_hash = hash_password(password)
        user_id = database.execute_insert(
            "INSERT INTO users (name, email, password_hash, role, company) VALUES (%s, %s, %s, %s, %s)",
            (name, email, pwd_hash, role, company)
        )

        session.clear()
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['user_role'] = role
        session['company'] = company

        flash('Account created successfully! Welcome to AI HR Recruitment Assistant.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('register.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = database.fetch_one("SELECT id, name, email, role, company, created_at FROM users WHERE id = %s", (session['user_id'],))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        company = request.form.get('company', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')

        if not name:
            flash('Name cannot be empty.', 'danger')
            return render_template('profile.html', user=user)

        database.execute_query("UPDATE users SET name = %s, company = %s WHERE id = %s", (name, company, session['user_id']))
        session['user_name'] = name
        session['company'] = company

        if new_password:
            full_user = database.fetch_one("SELECT password_hash FROM users WHERE id = %s", (session['user_id'],))
            if not verify_password(full_user['password_hash'], current_password):
                flash('Current password incorrect. Password was not changed.', 'danger')
                return render_template('profile.html', user=user)
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
                return render_template('profile.html', user=user)
            database.execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (hash_password(new_password), session['user_id']))
            flash('Profile and password updated successfully.', 'success')
        else:
            flash('Profile updated successfully.', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=user)

# ==================== JSON REST API ====================

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required.'}), 400

    user = database.fetch_one("SELECT * FROM users WHERE LOWER(email) = %s", (email,))
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

    session.clear()
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['user_role'] = user.get('role', 'HR Manager')
    session['company'] = user.get('company', 'Acme Corp')

    return jsonify({
        'success': True,
        'message': 'Login successful.',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user.get('role'),
            'company': user.get('company')
        }
    })

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    company = data.get('company', 'Acme Corp')
    role = data.get('role', 'HR Manager')

    is_valid, err = validate_registration(name, email, password, confirm_password)
    if not is_valid:
        return jsonify({'success': False, 'error': err}), 400

    existing = database.fetch_one("SELECT id FROM users WHERE LOWER(email) = %s", (email,))
    if existing:
        return jsonify({'success': False, 'error': 'Account with this email already exists.'}), 409

    pwd_hash = hash_password(password)
    user_id = database.execute_insert(
        "INSERT INTO users (name, email, password_hash, role, company) VALUES (%s, %s, %s, %s, %s)",
        (name, email, pwd_hash, role, company)
    )

    session.clear()
    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    session['user_role'] = role
    session['company'] = company

    return jsonify({
        'success': True,
        'message': 'Account registered successfully.',
        'user_id': user_id
    }), 201

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@auth_bp.route('/api/me', methods=['GET'])
@login_required
def api_me():
    user = database.fetch_one("SELECT id, name, email, role, company, created_at FROM users WHERE id = %s", (session['user_id'],))
    return jsonify({'success': True, 'user': user})

