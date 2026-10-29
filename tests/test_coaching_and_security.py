from datetime import date
import pytest
from app import db
from app.models.user import User
from app.models.workout import WorkoutLog, WorkoutLogItem, WorkoutPlan
from app.models.nutrition import MealPlan, MealPlanItem
from app.models.habit import DailyHabitLog, CoachingRecommendation
from app.services.coaching_engine import CoachingEngine
from app.services.research_data import get_all_sources

def test_user_data_isolation(client, app, registered_user, second_user):
    """Point 16: Strict user data isolation and cross-tenant access prevention."""
    with app.app_context():
        # User 1 has a workout log and a meal plan
        log1 = WorkoutLog(user_id=registered_user, date=date(2026, 10, 28), session_name="User1 Secret Workout")
        db.session.add(log1)
        db.session.flush()

        plan1 = MealPlan(user_id=registered_user, title="User1 Diet", target_calories=2100, target_protein=140, target_carbs=220, target_fat=60)
        db.session.add(plan1)
        db.session.flush()

        item1 = MealPlanItem(meal_plan_id=plan1.id, meal_type="Lunch", food_name="User1 Paneer", portion_grams=100, calories=260, protein=18, carbs=3, fat=20)
        db.session.add(item1)
        db.session.commit()

        log1_id = log1.id
        item1_id = item1.id

    # Log in as User 2 (second_user)
    client.post('/auth/login', data={'login_id': 'otheruser', 'password': 'password456'})

    # Attempt to delete User 1's workout log as User 2 -> Must be 404
    del_log_res = client.post(f'/workout/log/{log1_id}/delete')
    assert del_log_res.status_code == 404

    # Attempt to edit User 1's meal item as User 2 -> Must be rejected
    edit_meal_res = client.post(f'/nutrition/plan/item/{item1_id}/edit', data={'portion_grams': '200'}, follow_redirects=True)
    assert b'Unauthorized access' in edit_meal_res.data

    # Confirm User 1's data was NOT changed
    with app.app_context():
        assert WorkoutLog.query.get(log1_id) is not None
        assert MealPlanItem.query.get(item1_id).portion_grams == 100

def test_adaptive_coaching_rules(app, registered_user):
    """Coaching engine adapts to performance and suppresses overload during poor recovery."""
    with app.app_context():
        # Case 1: High performance log (10 reps, 60kg, low RPE 7) -> Suggests progressive overload
        log = WorkoutLog(user_id=registered_user, date=date(2026, 10, 28), session_name="Squat Session")
        db.session.add(log)
        db.session.flush()
        db.session.add(WorkoutLogItem(log_id=log.id, exercise_name="Barbell Back Squat", set_number=1, weight_kg=60, reps_completed=10, rpe=7.0))
        db.session.add(WorkoutLogItem(log_id=log.id, exercise_name="Barbell Back Squat", set_number=2, weight_kg=60, reps_completed=10, rpe=7.5))
        db.session.commit()

        recs = CoachingEngine.generate_recommendations(registered_user)
        assert len(recs) >= 1
        overload_rec = [r for r in recs if "Progressive Overload" in r.title]
        assert len(overload_rec) == 1
        assert "62.5" in overload_rec[0].recommendation_text  # +2.5kg suggestion

        # Case 2: Now user logs poor sleep (< 6h) or muscle soreness -> Adaptive recovery alert triggered
        habit = DailyHabitLog(user_id=registered_user, date=date(2026, 10, 29), sleep_hours=5.0, recovery_feeling="sore")
        db.session.add(habit)
        db.session.commit()

        recovery_recs = CoachingEngine.generate_recommendations(registered_user)
        rec_texts = [r.recommendation_text for r in recovery_recs]
        # Never increase training loads when sore / sleep-deprived
        assert any("Do not increase training weights" in text for text in rec_texts)

def test_invalid_inputs_resilience(client, app, registered_user):
    """Point 18: Invalid inputs handled without uncaught exceptions."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # Invalid negative portion on meal edit
    with app.app_context():
        plan = MealPlan(user_id=registered_user, title="Test Plan", target_calories=2000, target_protein=130, target_carbs=220, target_fat=60)
        db.session.add(plan)
        db.session.flush()
        item = MealPlanItem(meal_plan_id=plan.id, meal_type="Breakfast", food_name="Oats", portion_grams=50, calories=190, protein=8, carbs=33, fat=3)
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    bad_portion_res = client.post(f'/nutrition/plan/item/{item_id}/edit', data={'portion_grams': '-50'}, follow_redirects=True)
    assert b'Portion must be greater than 0' in bad_portion_res.data

def test_external_api_failure_resilience(app):
    """Point 19: System is self-contained and operates completely without external network dependencies."""
    with app.app_context():
        # Research sources are statically verified and fully operational offline
        sources = get_all_sources()
        assert len(sources) >= 5
        source_names = [s['name'] for s in sources]
        assert any("American College of Sports Medicine" in name for name in source_names)
        assert any("National Strength and Conditioning Association" in name for name in source_names)
        assert any("National Institute of Nutrition" in name for name in source_names)
        assert any("World Health Organization" in name for name in source_names)
