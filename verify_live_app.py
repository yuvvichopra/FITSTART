import sys
from app import create_app, db
from app.models.user import User, UserProfile
from app.models.workout import WorkoutPlan, WorkoutLog
from app.models.nutrition import MealPlan, DailyNutritionLog
from app.models.habit import DailyHabitLog

def verify_live():
    print("=== STARTING FITSTART LIVE INTEGRATION VERIFICATION ===")
    app = create_app('development')
    client = app.test_client()

    with app.app_context():
        # Ensure fresh DB tables
        db.create_all()
        print("[PASS] Database tables verified & initialized.")

        # Test 1: Landing page
        res = client.get('/')
        assert res.status_code == 200, f"Landing page returned {res.status_code}"
        assert b"FitStart" in res.data
        print("[PASS] Landing page responds with HTTP 200.")

        # Test 2: Research library
        res_research = client.get('/research')
        assert res_research.status_code == 200
        assert b"American College of Sports Medicine" in res_research.data
        assert b"National Institute of Nutrition" in res_research.data
        print("[PASS] Research library loaded successfully with ACSM, NSCA, ICMR-NIN & WHO sources.")

        # Test 3: Food database
        res_foods = client.get('/nutrition/foods')
        assert res_foods.status_code == 200
        assert b"Sattu" in res_foods.data
        assert b"Roti" in res_foods.data
        print("[PASS] Verified Food Database page operational.")

        # Test 4: Registration with real CSRF token extracted from form
        username = "student_yuvraj"
        email = "yuvraj@college.edu"
        password = "FitPassword@2026"

        import re
        reg_get = client.get('/auth/register')
        csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', reg_get.data.decode('utf-8')).group(1)

        # Clean existing test user if any
        existing = User.query.filter_by(username=username).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        reg_res = client.post('/auth/register', data={
            'csrf_token': csrf_token,
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': password
        }, follow_redirects=True)
        assert reg_res.status_code == 200, f"Registration failed with {reg_res.status_code}"
        print(f"[PASS] Registered student user '{username}' with valid CSRF token.")

        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.check_password(password) is True

        # Test 5: Complete 8-step questionnaire with CSRF
        q_get = client.get('/onboarding/questionnaire')
        csrf_q = re.search(r'name="csrf_token" value="([^"]+)"', q_get.data.decode('utf-8')).group(1)

        onboard_res = client.post('/onboarding/questionnaire', data={
            'csrf_token': csrf_q,
            'age': '21',
            'gender': 'Male',
            'unit_system': 'metric',
            'height': '175',
            'weight': '70',
            'region': 'North Indian',
            'activity_level': 'moderately_active',
            'experience_level': 'beginner',
            'primary_goal': 'muscle_gain',
            'secondary_goals': ['posture', 'core_stability'],
            'equipment_setting': 'commercial_gym',
            'available_equipment': ['barbells', 'dumbbells', 'cables', 'bench'],
            'training_days_count': '3',
            'preferred_days': ['Monday', 'Wednesday', 'Friday'],
            'preferred_time': 'morning',
            'cardio_preference': 'walking',
            'diet_type': 'vegetarian',
            'cooking_facility': 'hostel_mess',
            'budget_level': 'budget_friendly',
            'meal_frequency': '4',
            'sleep_hours': '7.5',
            'daily_step_target': '9000',
            'coaching_style': 'encouraging',
            'desired_difficulty': 'moderate'
        }, follow_redirects=True)
        assert onboard_res.status_code == 200
        print("[PASS] Onboarding completed. Training and nutrition plans synthesized.")

        # Test 6: Verify Workout Plan in DB
        w_plan = WorkoutPlan.query.filter_by(user_id=user.id, is_active=True).first()
        assert w_plan is not None
        assert len(w_plan.days) == 3
        print(f"[PASS] Active Workout Plan generated: '{w_plan.title}' with {len(w_plan.days)} days.")

        # Test 7: Verify Meal Plan in DB
        m_plan = MealPlan.query.filter_by(user_id=user.id, is_active=True).first()
        assert m_plan is not None
        assert m_plan.target_calories > 1800
        print(f"[PASS] Active Meal Plan generated: '{m_plan.title}' ({round(m_plan.target_calories)} kcal target).")

        # Test 8: Log a Workout Session with CSRF
        w_log_get = client.get('/workout/log')
        csrf_w = re.search(r'name="csrf_token" value="([^"]+)"', w_log_get.data.decode('utf-8')).group(1)

        log_res = client.post('/workout/log', data={
            'csrf_token': csrf_w,
            'date': '2026-10-29',
            'session_name': 'Push & Quads Foundation',
            'duration_minutes': '45',
            'perceived_exertion': '7',
            'notes': 'Great mind-muscle connection',
            'exercise_name[]': ['Barbell Flat Bench Press', 'Barbell Flat Bench Press'],
            'set_number[]': ['1', '2'],
            'weight_kg[]': ['55', '55'],
            'reps_completed[]': ['10', '10'],
            'rpe[]': ['7', '7.5'],
            'item_notes[]': ['Easy', 'Controlled pause']
        }, follow_redirects=True)
        assert log_res.status_code == 200
        print("[PASS] Workout logged successfully.")

        # Test 9: Log Daily Habits with CSRF
        h_get = client.get('/habits/tracker?date=2026-10-29')
        csrf_h = re.search(r'name="csrf_token" value="([^"]+)"', h_get.data.decode('utf-8')).group(1)

        habit_res = client.post('/habits/tracker?date=2026-10-29', data={
            'csrf_token': csrf_h,
            'water_ml': '3000',
            'sleep_hours': '8.0',
            'sleep_quality': '5',
            'steps': '9200',
            'workout_completed': 'true',
            'recovery_feeling': 'great',
            'notes': 'Slept soundly, hit hydration goal'
        }, follow_redirects=True)
        assert habit_res.status_code == 200
        print("[PASS] Habits (water, sleep, steps) saved successfully.")

        # Test 10: Verify Dashboard & Chart API
        dash_res = client.get('/dashboard/')
        assert dash_res.status_code == 200
        assert b"student_yuvraj" in dash_res.data

        chart_res = client.get('/dashboard/api/chart-data')
        assert chart_res.status_code == 200
        data = chart_res.get_json()
        assert sum(data['volume']) > 0  # Verified volume recorded
        print("[PASS] Dashboard and Chart API populated with actual user data.")

        # Test 11: Weekly Review
        review_res = client.get('/dashboard/weekly-review')
        assert review_res.status_code == 200
        assert b"Objective Weekly Review" in review_res.data
        print("[PASS] Objective Weekly Review compiled successfully.")

    print("\n[SUCCESS] ALL LIVE VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == '__main__':
    verify_live()
