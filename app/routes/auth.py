from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, UserProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', username=username, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html', username=username, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', username=username, email=email)

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html', email=email)

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please log in.', 'danger')
            return render_template('auth/register.html', username=username)

        # Create user & initial empty profile
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Welcome to FitStart. Please complete your onboarding.', 'success')
        return redirect(url_for('onboarding.questionnaire'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not login_id or not password:
            flash('Please enter both your username/email and password.', 'danger')
            return render_template('auth/login.html')

        # Allow login via username or email
        user = User.query.filter((User.username == login_id) | (User.email == login_id.lower())).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')

            if user.profile and not user.profile.onboarding_completed:
                return redirect(url_for('onboarding.questionnaire'))

            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))
