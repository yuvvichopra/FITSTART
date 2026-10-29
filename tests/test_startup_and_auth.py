import pytest
from app import create_app, db
from app.models.user import User, UserProfile

def test_application_startup(app):
    """Point 1: Application startup and configuration loading."""
    assert app is not None
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'

def test_registration_and_login(client, app):
    """Point 2: Registration, password hashing, and login/logout flow."""
    # Register new user
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@fitstart.test',
        'password': 'securepassword123',
        'confirm_password': 'securepassword123'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@fitstart.test'
        assert user.password_hash != 'securepassword123'  # properly hashed
        assert user.check_password('securepassword123') is True
        assert user.check_password('wrongpassword') is False
        assert user.profile is not None  # Profile initialized

    # Logout
    logout_res = client.get('/auth/logout', follow_redirects=True)
    assert logout_res.status_code == 200

    # Login with valid credentials
    login_res = client.post('/auth/login', data={
        'login_id': 'newuser',
        'password': 'securepassword123'
    }, follow_redirects=True)
    assert login_res.status_code == 200

    # Logout to test invalid password login
    client.get('/auth/logout')

    # Login with invalid password
    bad_login = client.post('/auth/login', data={
        'login_id': 'newuser',
        'password': 'incorrectpassword'
    }, follow_redirects=True)
    assert b'Invalid username/email or password' in bad_login.data

def test_duplicate_registration_prevention(client, app, registered_user):
    """Prevents duplicate username or email registrations."""
    # Attempt duplicate username
    res1 = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'another@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'Username is already taken' in res1.data

    # Attempt duplicate email
    res2 = client.post('/auth/register', data={
        'username': 'differentuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'Email is already registered' in res2.data

def test_profile_persistence(client, app, registered_user):
    """Point 3: Profile persistence across sessions."""
    # Log in as registered user
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # Update profile
    response = client.post('/onboarding/profile', data={
        'age': '23',
        'height_cm': '176.5',
        'weight_kg': '72.0',
        'activity_level': 'very_active',
        'region': 'North Indian',
        'primary_goal': 'strength',
        'equipment_setting': 'commercial_gym',
        'training_days_count': '4',
        'diet_type': 'vegetarian',
        'cooking_facility': 'full_kitchen',
        'budget_level': 'moderate',
        'sleep_hours': '8.0',
        'daily_step_target': '10000',
        'coaching_style': 'analytical'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        user = User.query.get(registered_user)
        assert user.profile.age == 23
        assert user.profile.height_cm == 176.5
        assert user.profile.weight_kg == 72.0
        assert user.profile.primary_goal == 'strength'
        assert user.profile.training_days_count == 4
        assert user.profile.activity_level == 'very_active'

def test_questionnaire_validation(client, app, registered_user):
    """Point 4: Questionnaire validation of inputs."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # Submit valid questionnaire
    valid_res = client.post('/onboarding/questionnaire', data={
        'age': '24',
        'gender': 'Male',
        'unit_system': 'metric',
        'height': '178',
        'weight': '74',
        'region': 'North Indian',
        'activity_level': 'moderately_active',
        'experience_level': 'beginner',
        'primary_goal': 'muscle_gain',
        'equipment_setting': 'commercial_gym',
        'training_days_count': '3',
        'diet_type': 'vegetarian',
        'cooking_facility': 'hostel_mess',
        'budget_level': 'moderate',
        'meal_frequency': '3',
        'sleep_hours': '7.5',
        'daily_step_target': '8500',
        'coaching_style': 'encouraging',
        'desired_difficulty': 'moderate'
    }, follow_redirects=True)
    assert valid_res.status_code == 200

    with app.app_context():
        user = User.query.get(registered_user)
        assert user.profile.onboarding_completed is True
        assert user.profile.height_cm == 178.0
        assert user.profile.weight_kg == 74.0
        # Active workout plan and meal plan generated
        assert user.workout_plans.count() >= 1
        assert user.meal_plans.count() >= 1
