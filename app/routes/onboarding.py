from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import UserProfile
from app.models.workout import WorkoutPlan
from app.models.nutrition import MealPlan
from app.services.workout_engine import WorkoutEngine
from app.services.nutrition_engine import NutritionEngine

onboarding_bp = Blueprint('onboarding', __name__)

@onboarding_bp.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        try:
            # 1. Personal Information
            profile.age = int(request.form.get('age', 22))
            profile.gender = request.form.get('gender')
            profile.unit_system = request.form.get('unit_system', 'metric')
            
            raw_height = float(request.form.get('height', 170))
            raw_weight = request.form.get('weight')
            raw_weight = float(raw_weight) if raw_weight and raw_weight.strip() else None

            # Unit conversion if imperial
            if profile.unit_system == 'imperial':
                profile.height_cm = round(raw_height * 2.54, 1)  # inches to cm
                profile.weight_kg = round(raw_weight * 0.453592, 1) if raw_weight else None
            else:
                profile.height_cm = round(raw_height, 1)
                profile.weight_kg = round(raw_weight, 1) if raw_weight else None

            profile.region = request.form.get('region', 'North Indian')
            profile.activity_level = request.form.get('activity_level', 'moderately_active')

            # 2. Experience
            profile.experience_level = request.form.get('experience_level', 'beginner')
            profile.training_history = request.form.get('training_history', '')
            profile.previous_structured_training = request.form.get('previous_structured_training') == 'yes'
            profile.exercise_confidence = int(request.form.get('exercise_confidence', 3))
            profile.current_training_frequency = int(request.form.get('current_training_frequency', 0))
            profile.preferred_session_length = int(request.form.get('preferred_session_length', 45))

            # 3. Goals
            profile.primary_goal = request.form.get('primary_goal', 'general_fitness')
            profile.secondary_goals = request.form.getlist('secondary_goals')

            # 4. Equipment
            profile.equipment_setting = request.form.get('equipment_setting', 'commercial_gym')
            profile.available_equipment = request.form.getlist('available_equipment')

            # 5. Schedule
            profile.training_days_count = int(request.form.get('training_days_count', 3))
            profile.preferred_days = request.form.getlist('preferred_days')
            profile.preferred_time = request.form.get('preferred_time', 'morning')
            profile.cardio_preference = request.form.get('cardio_preference', 'walking')
            profile.schedule_constraints = request.form.get('schedule_constraints', '')

            # 6. Diet
            profile.diet_type = request.form.get('diet_type', 'vegetarian')
            profile.allergies = request.form.getlist('allergies')
            profile.food_intolerances = request.form.get('food_intolerances', '')
            dislikes_str = request.form.get('food_dislikes', '')
            profile.food_dislikes = [d.strip() for d in dislikes_str.split(',') if d.strip()]
            profile.budget_level = request.form.get('budget_level', 'moderate')
            profile.meal_frequency = int(request.form.get('meal_frequency', 3))
            profile.cooking_facility = request.form.get('cooking_facility', 'hostel_mess')
            profile.preferred_protein_sources = request.form.getlist('preferred_protein_sources')
            profile.meal_timing = request.form.get('meal_timing', 'standard')

            # 7. Recovery & Safety
            profile.sleep_hours = float(request.form.get('sleep_hours', 7.0))
            profile.daily_step_target = int(request.form.get('daily_step_target', 8000))
            profile.recovery_preferences = request.form.getlist('recovery_preferences')
            profile.pain_movements = request.form.getlist('pain_movements')
            profile.physical_restrictions = request.form.get('physical_restrictions', '')
            profile.medical_conditions = request.form.get('medical_conditions', '')

            # 8. Additional Preferences
            profile.priority_muscle_groups = request.form.getlist('priority_muscle_groups')
            profile.coaching_style = request.form.get('coaching_style', 'encouraging')
            profile.desired_difficulty = request.form.get('desired_difficulty', 'moderate')

            profile.onboarding_completed = True
            db.session.commit()

            # Archive previous active plans if any exist
            WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})
            MealPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})

            # Generate new personalized plans
            workout_plan = WorkoutEngine.generate_program(current_user.id, profile)
            db.session.add(workout_plan)

            meal_plan = NutritionEngine.generate_meal_plan(current_user.id, profile)
            db.session.add(meal_plan)

            db.session.commit()

            flash('Your personalized FitStart training and nutrition plans have been engineered!', 'success')
            return redirect(url_for('dashboard.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error processing onboarding: {str(e)}. Please check your inputs.', 'danger')

    return render_template('onboarding/questionnaire.html', profile=profile)


@onboarding_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        try:
            profile.age = int(request.form.get('age', profile.age or 22))
            profile.gender = request.form.get('gender', profile.gender)
            profile.height_cm = float(request.form.get('height_cm', profile.height_cm or 170.0))
            w = request.form.get('weight_kg')
            profile.weight_kg = float(w) if w and w.strip() else profile.weight_kg
            profile.region = request.form.get('region', profile.region)
            profile.activity_level = request.form.get('activity_level', profile.activity_level)
            profile.experience_level = request.form.get('experience_level', profile.experience_level)
            profile.primary_goal = request.form.get('primary_goal', profile.primary_goal)
            profile.equipment_setting = request.form.get('equipment_setting', profile.equipment_setting)
            profile.training_days_count = int(request.form.get('training_days_count', profile.training_days_count or 3))
            profile.diet_type = request.form.get('diet_type', profile.diet_type)
            profile.cooking_facility = request.form.get('cooking_facility', profile.cooking_facility)
            profile.budget_level = request.form.get('budget_level', profile.budget_level)
            profile.sleep_hours = float(request.form.get('sleep_hours', profile.sleep_hours or 7.0))
            profile.daily_step_target = int(request.form.get('daily_step_target', profile.daily_step_target or 8000))
            profile.coaching_style = request.form.get('coaching_style', profile.coaching_style)
            profile.physical_restrictions = request.form.get('physical_restrictions', profile.physical_restrictions)
            profile.medical_conditions = request.form.get('medical_conditions', profile.medical_conditions)

            # Option to regenerate plans directly
            if request.form.get('regenerate_plans') == 'true':
                WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})
                MealPlan.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})

                new_workout = WorkoutEngine.generate_program(current_user.id, profile)
                new_meal = NutritionEngine.generate_meal_plan(current_user.id, profile)
                db.session.add(new_workout)
                db.session.add(new_meal)
                flash('Profile updated and fresh personalized plans regenerated!', 'success')
            else:
                flash('Profile settings updated successfully.', 'success')

            db.session.commit()
            return redirect(url_for('onboarding.profile'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('onboarding/profile.html', profile=profile)
