import pytest
from app import db
from app.models.user import User, UserProfile
from app.models.workout import WorkoutPlan
from app.services.workout_engine import WorkoutEngine

def test_different_workout_goals(app):
    """Point 5: Different workout goals change rep targets, RPE, and set architecture."""
    with app.app_context():
        # Strength Goal
        p_strength = UserProfile(
            primary_goal='strength',
            training_days_count=3,
            experience_level='consistent',
            equipment_setting='commercial_gym'
        )
        plan_strength = WorkoutEngine.generate_program(1, p_strength)
        first_ex_strength = plan_strength.days[0].exercises[0]
        assert "5-6" in first_ex_strength.reps
        assert "8" in first_ex_strength.rpe_target

        # Hypertrophy Goal
        p_hyp = UserProfile(
            primary_goal='muscle_gain',
            training_days_count=3,
            experience_level='beginner',
            equipment_setting='commercial_gym'
        )
        plan_hyp = WorkoutEngine.generate_program(1, p_hyp)
        first_ex_hyp = plan_hyp.days[0].exercises[0]
        assert "8-10" in first_ex_hyp.reps or "8-12" in first_ex_hyp.reps

        # Conservative Return to Training Goal
        p_return = UserProfile(
            primary_goal='return_to_training',
            training_days_count=2,
            experience_level='beginner',
            equipment_setting='commercial_gym'
        )
        plan_return = WorkoutEngine.generate_program(1, p_return)
        assert plan_return.split_type == 'conservative_return'
        first_ex_ret = plan_return.days[0].exercises[0]
        assert first_ex_ret.sets == 2  # Lower conservative volume
        assert "6" in first_ex_ret.rpe_target  # Low RPE safeguard

def test_equipment_based_substitutions(app):
    """Point 6: Equipment constraints and pain-based substitutions."""
    with app.app_context():
        # Bodyweight only
        p_calisthenics = UserProfile(
            primary_goal='general_fitness',
            training_days_count=3,
            equipment_setting='bodyweight_only',
            available_equipment=['bodyweight']
        )
        plan_calisthenics = WorkoutEngine.generate_program(1, p_calisthenics)
        assert plan_calisthenics.split_type == 'calisthenics_minimal'
        # Confirm no heavy barbells required
        for day in plan_calisthenics.days:
            for ex in day.exercises:
                assert ex.equipment == 'Bodyweight'

        # Pain movements adaptation: Knee pain substitutions
        p_knee_pain = UserProfile(
            primary_goal='muscle_gain',
            training_days_count=3,
            equipment_setting='commercial_gym',
            pain_movements=['knee_squats']
        )
        plan_knee = WorkoutEngine.generate_program(1, p_knee_pain)
        day1_exercises = [ex.exercise_name for ex in plan_knee.days[0].exercises]
        assert any("Knee-Friendly" in name or "Box Goblet" in name for name in day1_exercises)

        # Pain movements adaptation: Shoulder pain substitutions
        p_shoulder_pain = UserProfile(
            primary_goal='strength',
            training_days_count=3,
            equipment_setting='commercial_gym',
            pain_movements=['shoulder_overhead_press']
        )
        plan_shoulder = WorkoutEngine.generate_program(1, p_shoulder_pain)
        day2_exercises = [ex.exercise_name for ex in plan_shoulder.days[1].exercises]
        assert any("Neutral" in name or "Floor Press" in name or "Face Pull" in name for name in day2_exercises)

def test_different_training_schedules(app):
    """Point 7: Different training schedules (2, 3, 4, 5, 6 days/week)."""
    with app.app_context():
        # 2 Days -> Full Body 2-Day
        p2 = UserProfile(training_days_count=2, equipment_setting='commercial_gym')
        plan2 = WorkoutEngine.generate_program(1, p2)
        assert plan2.split_type == 'full_body_2day'
        assert len(plan2.days) == 2

        # 3 Days -> Full Body 3-Day
        p3 = UserProfile(training_days_count=3, equipment_setting='commercial_gym')
        plan3 = WorkoutEngine.generate_program(1, p3)
        assert plan3.split_type == 'full_body_3day'
        assert len(plan3.days) == 3

        # 4 Days -> Upper / Lower
        p4 = UserProfile(training_days_count=4, equipment_setting='commercial_gym')
        plan4 = WorkoutEngine.generate_program(1, p4)
        assert plan4.split_type == 'upper_lower_4day'
        assert len(plan4.days) == 4

        # 6 Days -> Push / Pull / Legs
        p6 = UserProfile(training_days_count=6, equipment_setting='commercial_gym')
        plan6 = WorkoutEngine.generate_program(1, p6)
        assert plan6.split_type == 'ppl_6day'
        assert len(plan6.days) == 6

def test_plan_versioning_and_restoration(client, app, registered_user):
    """Point 15: Plan versioning, regeneration, and restoration."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # 1. Regenerate plan
    res1 = client.post('/workout/plan/regenerate', follow_redirects=True)
    assert res1.status_code == 200

    with app.app_context():
        user = User.query.get(registered_user)
        assert user.workout_plans.count() == 1
        plan1_id = user.workout_plans.first().id
        assert user.workout_plans.first().version == 1

    # 2. Regenerate second plan
    res2 = client.post('/workout/plan/regenerate', follow_redirects=True)
    assert res2.status_code == 200

    with app.app_context():
        user = User.query.get(registered_user)
        assert user.workout_plans.count() == 2
        active_plan = WorkoutPlan.query.filter_by(user_id=registered_user, is_active=True).first()
        assert active_plan.version == 2

    # 3. Restore Plan 1 as active
    res3 = client.post(f'/workout/plan/{plan1_id}/restore', follow_redirects=True)
    assert res3.status_code == 200

    with app.app_context():
        plan1 = WorkoutPlan.query.get(plan1_id)
        assert plan1.is_active is True
        plan2 = WorkoutPlan.query.filter_by(user_id=registered_user, version=2).first()
        assert plan2.is_active is False
