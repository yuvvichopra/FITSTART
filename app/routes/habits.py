from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.habit import DailyHabitLog
from app.services.coaching_engine import CoachingEngine

habits_bp = Blueprint('habits', __name__)

@habits_bp.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    try:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        current_date = datetime.utcnow().date()

    habit_log = DailyHabitLog.query.filter_by(
        user_id=current_user.id,
        date=current_date
    ).first()

    if request.method == 'POST':
        try:
            if not habit_log:
                habit_log = DailyHabitLog(
                    user_id=current_user.id,
                    date=current_date
                )
                db.session.add(habit_log)

            habit_log.water_ml = int(request.form.get('water_ml', 0))
            habit_log.sleep_hours = float(request.form.get('sleep_hours', 0.0))
            habit_log.sleep_quality = int(request.form.get('sleep_quality', 3))
            habit_log.steps = int(request.form.get('steps', 0))
            habit_log.workout_completed = request.form.get('workout_completed') == 'true' or request.form.get('workout_completed') == 'on'
            habit_log.recovery_feeling = request.form.get('recovery_feeling', 'moderate')
            habit_log.notes = request.form.get('notes', '').strip()

            db.session.commit()

            # Refresh adaptive coaching analysis
            CoachingEngine.generate_recommendations(current_user.id)

            flash(f'Habit log for {current_date.strftime("%B %d, %Y")} saved successfully!', 'success')
            return redirect(url_for('habits.tracker', date=current_date.strftime('%Y-%m-%d')))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving habits: {str(e)}', 'danger')

    # Fetch last 7 days of logs for quick history view
    recent_habits = DailyHabitLog.query.filter_by(user_id=current_user.id)\
        .order_by(DailyHabitLog.date.desc()).limit(7).all()

    step_target = current_user.profile.daily_step_target if current_user.profile else 8000

    return render_template(
        'habits/tracker.html',
        current_date=current_date.strftime('%Y-%m-%d'),
        habit_log=habit_log,
        recent_habits=recent_habits,
        step_target=step_target
    )
