from datetime import datetime, date
import pytest
from app import db
from app.models.user import User
from app.models.workout import WorkoutLog, WorkoutLogItem
from app.models.nutrition import DailyNutritionLog
from app.models.habit import DailyHabitLog
from app.services.coaching_engine import CoachingEngine

def test_workout_logging_and_pr_calculations(client, app, registered_user):
    """Point 12: Workout logging and 1RM calculation."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # Log a session with multiple sets
    res = client.post('/workout/log', data={
        'date': '2026-10-29',
        'session_name': 'Heavy Leg Day',
        'duration_minutes': '50',
        'perceived_exertion': '8',
        'notes': 'Great squat depth',
        'exercise_name[]': ['Barbell Back Squat', 'Barbell Back Squat'],
        'set_number[]': ['1', '2'],
        'weight_kg[]': ['80', '80'],
        'reps_completed[]': ['10', '10'],
        'rpe[]': ['8', '8.5'],
        'item_notes[]': ['Set 1 good', 'Set 2 tough']
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        log = WorkoutLog.query.filter_by(user_id=registered_user).first()
        assert log is not None
        assert log.session_name == 'Heavy Leg Day'
        assert len(log.items) == 2
        assert log.items[0].weight_kg == 80.0
        assert log.items[0].reps_completed == 10

        # Epley 1RM formula check: weight * (1 + reps/30) = 80 * (1 + 10/30) = 80 * 1.333 = 106.7 kg
        prs = CoachingEngine.get_user_prs(registered_user)
        assert 'Barbell Back Squat' in prs
        assert prs['Barbell Back Squat']['weight_kg'] == 80.0
        assert round(prs['Barbell Back Squat']['est_1rm'], 1) == 106.7

def test_habit_tracking_and_water_sleep(client, app, registered_user):
    """Point 13: Daily habit tracking (water, sleep, steps, recovery feeling)."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    res = client.post('/habits/tracker?date=2026-10-29', data={
        'water_ml': '2750',
        'sleep_hours': '8.0',
        'sleep_quality': '4',
        'steps': '9500',
        'workout_completed': 'true',
        'recovery_feeling': 'good',
        'notes': 'Hydrated well today'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        log = DailyHabitLog.query.filter_by(
            user_id=registered_user,
            date=date(2026, 10, 29)
        ).first()
        assert log is not None
        assert log.water_ml == 2750
        assert log.sleep_hours == 8.0
        assert log.steps == 9500
        assert log.workout_completed is True
        assert log.recovery_feeling == 'good'

def test_progress_dashboard_and_chart_data(client, app, registered_user):
    """Point 14: Progress calculations and chart data endpoint."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # Access chart data API
    api_res = client.get('/dashboard/api/chart-data')
    assert api_res.status_code == 200
    json_data = api_res.get_json()
    assert 'labels' in json_data
    assert 'volume' in json_data
    assert 'calories' in json_data
    assert 'water' in json_data
    assert 'sleep' in json_data
    assert len(json_data['labels']) == 10

def test_empty_datasets_handling(client, app, registered_user):
    """Point 20: Empty datasets and unlogged data handled gracefully."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # 1. Dashboard with zero logged sessions or meals should not crash
    dash_res = client.get('/dashboard/')
    assert dash_res.status_code == 200
    assert b'Welcome Back' in dash_res.data

    # 2. Weekly review with empty history should report honest gaps without division by zero
    rev_res = client.get('/dashboard/weekly-review')
    assert rev_res.status_code == 200
    assert b'No workout sessions were recorded' in rev_res.data
    assert b'Identified Tracking Gaps' in rev_res.data

    # 3. PRs on empty history
    with app.app_context():
        prs = CoachingEngine.get_user_prs(registered_user)
        assert prs == {}
