from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models.user import User, Admin
from dao.user_dao import UserDAO, AdminDAO

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            flash("Administrator access required. Please sign in to the Admin Portal.", "danger")
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return UserDAO.get_by_id(user_id)
    return None

def get_current_admin():
    admin_id = session.get('admin_id')
    if admin_id:
        return AdminDAO.get_by_id(admin_id)
    return None

@auth_bp.before_app_request
def load_logged_in_user():
    g.current_user = get_current_user()
    g.current_admin = get_current_admin()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')

        # Validation
        if not name or len(name) < 2:
            flash("Please enter a valid full name (minimum 2 characters).", "danger")
            return render_template('register.html', name=name, email=email)

        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "danger")
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', name=name, email=email)

        # Check existing user
        existing_user = UserDAO.get_by_email(email)
        if existing_user:
            flash("An account with this email address already exists. Please log in.", "warning")
            return redirect(url_for('auth.login'))

        # Create user
        password_hash = User.hash_password(password)
        user_id = UserDAO.create_user(name=name, email=email, password_hash=password_hash, role=role)

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = UserDAO.get_by_email(email)
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('login.html', email=email)

        if not user.is_active:
            flash("Your account has been deactivated. Please contact support.", "danger")
            return render_template('login.html', email=email)

        # Successful login
        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role

        flash(f"Welcome back, {user.name}!", "success")
        next_url = request.args.get('next')
        return redirect(next_url or url_for('user.dashboard'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('index'))
