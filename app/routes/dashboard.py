from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.workout import WorkoutPlan, WorkoutLog, WorkoutLogItem
from app.models.nutrition import MealPlan, DailyNutritionLog
from app.models.habit import DailyHabitLog, CoachingRecommendation
from app.services.coaching_engine import CoachingEngine

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())  # Monday of current week

    # 1. Active plans
    active_workout_plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    active_meal_plan = MealPlan.query.filter_by(user_id=current_user.id, is_active=True).first()

    # 2. Today's logs
    today_habits = DailyHabitLog.query.filter_by(user_id=current_user.id, date=today).first()
    today_nutrition = DailyNutritionLog.query.filter_by(user_id=current_user.id, date=today).all()

    today_cals = sum(n.calories for n in today_nutrition)
    today_protein = sum(n.protein for n in today_nutrition)

    # 3. Weekly workouts completed
    weekly_workout_count = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.date >= week_start
    ).count()

    # 4. Pending Coaching Recommendations
    pending_recs = CoachingRecommendation.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).order_by(CoachingRecommendation.created_at.desc()).limit(3).all()

    # 5. Personal records summary
    prs = CoachingEngine.get_user_prs(current_user.id)

    return render_template(
        'dashboard/index.html',
        today=today.strftime('%A, %B %d, %Y'),
        active_workout=active_workout_plan,
        active_nutrition=active_meal_plan,
        today_habits=today_habits,
        today_cals=round(today_cals),
        today_protein=round(today_protein, 1),
        weekly_workout_count=weekly_workout_count,
        pending_recs=pending_recs,
        prs_count=len(prs)
    )


@dashboard_bp.route('/recommendation/<int:rec_id>/status', methods=['POST'])
@login_required
def update_recommendation_status(rec_id):
    rec = CoachingRecommendation.query.filter_by(id=rec_id, user_id=current_user.id).first_or_404()
    new_status = request.form.get('status', 'ignored')
    if new_status in ['accepted', 'rejected', 'ignored']:
        rec.status = new_status
        db.session.commit()
        flash(f'Recommendation {new_status}. Adaptive engine updated.', 'info')
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/weekly-review')
@login_required
def weekly_review():
    today = datetime.utcnow().date()
    # Look back over last 7 days
    start_date = today - timedelta(days=6)

    # Fetch logs in window
    workout_logs = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.date >= start_date,
        WorkoutLog.date <= today
    ).order_by(WorkoutLog.date).all()

    habit_logs = DailyHabitLog.query.filter(
        DailyHabitLog.user_id == current_user.id,
        DailyHabitLog.date >= start_date,
        DailyHabitLog.date <= today
    ).order_by(DailyHabitLog.date).all()

    nutrition_logs = DailyNutritionLog.query.filter(
        DailyNutritionLog.user_id == current_user.id,
        DailyNutritionLog.date >= start_date,
        DailyNutritionLog.date <= today
    ).all()

    # Calculate metrics
    # 1. Workouts
    total_workouts = len(workout_logs)
    target_workouts = current_user.profile.training_days_count if current_user.profile else 3
    total_volume_kg = 0.0
    for w in workout_logs:
        for item in w.items:
            total_volume_kg += (item.weight_kg or 0.0) * (item.reps_completed or 0)

    # 2. Nutrition adherence
    nutrition_by_date = {}
    for n in nutrition_logs:
        nutrition_by_date.setdefault(n.date, []).append(n)

    days_food_logged = len(nutrition_by_date)
    avg_calories = 0.0
    avg_protein = 0.0
    if days_food_logged > 0:
        cals_list = [sum(item.calories for item in items) for items in nutrition_by_date.values()]
        prot_list = [sum(item.protein for item in items) for items in nutrition_by_date.values()]
        avg_calories = sum(cals_list) / days_food_logged
        avg_protein = sum(prot_list) / days_food_logged

    # 3. Habits
    days_habits_logged = len(habit_logs)
    avg_sleep = 0.0
    total_water = 0
    total_steps = 0
    if days_habits_logged > 0:
        sleeps = [h.sleep_hours for h in habit_logs if h.sleep_hours > 0]
        avg_sleep = (sum(sleeps) / len(sleeps)) if sleeps else 0.0
        total_water = sum(h.water_ml for h in habit_logs)
        total_steps = sum(h.steps for h in habit_logs)

    # 4. PRs
    prs = CoachingEngine.get_user_prs(current_user.id)

    # 5. Generate honest, objective feedback without fabrication
    insights = []
    gaps = []
    adjustments = []

    # Workout assessment
    if total_workouts >= target_workouts:
        insights.append(f"Outstanding discipline: you completed {total_workouts} out of your {target_workouts} scheduled sessions ({round(total_volume_kg)} kg total volume moved).")
    elif total_workouts > 0:
        insights.append(f"Consistent progress: you completed {total_workouts} out of {target_workouts} planned sessions.")
        adjustments.append("Consider scheduling workouts at consistent times (e.g. morning before classes) to hit full session frequency.")
    else:
        gaps.append(f"No workout sessions were recorded in the past 7 days. If you trained, be sure to log your sets so progressive overload can be calibrated.")

    # Nutrition assessment
    active_meal = MealPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    target_cals = active_meal.target_calories if active_meal else 2000.0

    if days_food_logged >= 5:
        cal_diff = avg_calories - target_cals
        if abs(cal_diff) <= 150:
            insights.append(f"Precision nutrition adherence: average daily intake was {round(avg_calories)} kcal (within 5% of your {round(target_cals)} kcal target).")
        elif cal_diff < -200:
            insights.append(f"Your recorded intake averaged {round(avg_calories)} kcal, notably lower than your target of {round(target_cals)} kcal.")
            adjustments.append("Ensure adequate daily fueling to sustain resistance training performance and prevent muscle loss.")
        else:
            insights.append(f"Your recorded intake averaged {round(avg_calories)} kcal (+{round(cal_diff)} kcal above target).")
    elif days_food_logged > 0:
        gaps.append(f"Food intake was recorded on only {days_food_logged} of 7 days. Note: unlogged days are NOT assumed to be zero food; more consistent tracking will improve caloric precision.")
    else:
        gaps.append("No meals were logged this week. Tracking even 3-4 days gives valuable baseline data.")

    # Sleep & recovery assessment
    if days_habits_logged >= 4:
        if avg_sleep >= 7.0:
            insights.append(f"Healthy restorative sleep: averaged {round(avg_sleep, 1)} hours nightly, optimizing hormonal and muscular repair.")
        else:
            insights.append(f"Sleep averaged {round(avg_sleep, 1)} hours nightly (below the 7-9h optimal athletic recovery window).")
            adjustments.append("Aim to shift bedtime 30-45 minutes earlier to accelerate neuromuscular recovery.")
    else:
        gaps.append(f"Daily habits were logged on {days_habits_logged} days. Tracking sleep and hydration helps flag fatigue early.")

    return render_template(
        'dashboard/weekly_review.html',
        start_date=start_date.strftime('%b %d'),
        end_date=today.strftime('%b %d, %Y'),
        total_workouts=total_workouts,
        target_workouts=target_workouts,
        total_volume_kg=round(total_volume_kg),
        days_food_logged=days_food_logged,
        avg_calories=round(avg_calories),
        target_cals=round(target_cals),
        avg_protein=round(avg_protein, 1),
        days_habits_logged=days_habits_logged,
        avg_sleep=round(avg_sleep, 1),
        insights=insights,
        gaps=gaps,
        adjustments=adjustments,
        prs=prs
    )


@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    today = datetime.utcnow().date()
    days_range = 10
    dates = [today - timedelta(days=i) for i in range(days_range - 1, -1, -1)]
    date_labels = [d.strftime('%b %d') for d in dates]

    # Fetch workout volume by date
    workout_logs = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.date >= dates[0]
    ).all()
    volume_by_date = {d: 0.0 for d in dates}
    for w in workout_logs:
        if w.date in volume_by_date:
            vol = sum((item.weight_kg or 0.0) * (item.reps_completed or 0) for item in w.items)
            volume_by_date[w.date] += vol

    # Fetch nutrition calories by date
    nutrition_logs = DailyNutritionLog.query.filter(
        DailyNutritionLog.user_id == current_user.id,
        DailyNutritionLog.date >= dates[0]
    ).all()
    cals_by_date = {d: 0.0 for d in dates}
    prot_by_date = {d: 0.0 for d in dates}
    for n in nutrition_logs:
        if n.date in cals_by_date:
            cals_by_date[n.date] += n.calories
            prot_by_date[n.date] += n.protein

    # Fetch water & sleep by date
    habit_logs = DailyHabitLog.query.filter(
        DailyHabitLog.user_id == current_user.id,
        DailyHabitLog.date >= dates[0]
    ).all()
    water_by_date = {d: 0 for d in dates}
    sleep_by_date = {d: 0.0 for d in dates}
    for h in habit_logs:
        if h.date in water_by_date:
            water_by_date[h.date] = h.water_ml
            sleep_by_date[h.date] = h.sleep_hours

    active_meal = MealPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    target_cals = active_meal.target_calories if active_meal else 2000.0

    return jsonify({
        'labels': date_labels,
        'volume': [round(volume_by_date[d]) for d in dates],
        'calories': [round(cals_by_date[d]) for d in dates],
        'protein': [round(prot_by_date[d], 1) for d in dates],
        'target_calories': [round(target_cals)] * len(dates),
        'water': [water_by_date[d] for d in dates],
        'sleep': [sleep_by_date[d] for d in dates]
    })
