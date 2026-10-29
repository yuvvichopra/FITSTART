from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.workout import WorkoutPlan, WorkoutDay, WorkoutExercise, WorkoutLog, WorkoutLogItem
from app.services.workout_engine import WorkoutEngine
from app.services.coaching_engine import CoachingEngine

workout_bp = Blueprint('workout', __name__)

@workout_bp.route('/plan')
@login_required
def plan():
    active_plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_plan and current_user.profile:
        # Auto-generate if missing
        active_plan = WorkoutEngine.generate_program(current_user.id, current_user.profile)
        db.session.add(active_plan)
        db.session.commit()

    return render_template('workout/plan.html', plan=active_plan)


@workout_bp.route('/plan/regenerate', methods=['POST'])
@login_required
def regenerate_plan():
    profile = current_user.profile
    if not profile:
        flash('Please complete your profile before generating a plan.', 'warning')
        return redirect(url_for('onboarding.questionnaire'))

    # Deactivate current plan while preserving it in history
    current_plans = WorkoutPlan.query.filter_by(user_id=current_user.id).all()
    for p in current_plans:
        p.is_active = False

    new_version = len(current_plans) + 1
    new_plan = WorkoutEngine.generate_program(current_user.id, profile)
    new_plan.version = new_version
    new_plan.is_active = True
    db.session.add(new_plan)
    db.session.commit()

    flash(f'New workout program (Version {new_version}) generated successfully!', 'success')
    return redirect(url_for('workout.plan'))


@workout_bp.route('/plan/history')
@login_required
def plan_history():
    plans = WorkoutPlan.query.filter_by(user_id=current_user.id).order_by(WorkoutPlan.created_at.desc()).all()
    return render_template('workout/history.html', plans=plans)


@workout_bp.route('/plan/<int:plan_id>/restore', methods=['POST'])
@login_required
def restore_plan(plan_id):
    target_plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()

    # Deactivate other plans
    WorkoutPlan.query.filter_by(user_id=current_user.id).update({'is_active': False})
    target_plan.is_active = True
    db.session.commit()

    flash(f'Workout program "{target_plan.title}" restored as active!', 'success')
    return redirect(url_for('workout.plan'))


@workout_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_workout():
    if request.method == 'POST':
        try:
            date_str = request.form.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
            session_name = request.form.get('session_name', 'Workout Session').strip()
            duration_minutes = int(request.form.get('duration_minutes', 45))
            rpe = int(request.form.get('perceived_exertion', 7))
            notes = request.form.get('notes', '').strip()

            log_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            workout_log = WorkoutLog(
                user_id=current_user.id,
                date=log_date,
                session_name=session_name,
                duration_minutes=duration_minutes,
                perceived_exertion=rpe,
                notes=notes
            )
            db.session.add(workout_log)
            db.session.flush()

            # Process exercises and sets
            exercise_names = request.form.getlist('exercise_name[]')
            set_numbers = request.form.getlist('set_number[]')
            weights = request.form.getlist('weight_kg[]')
            reps = request.form.getlist('reps_completed[]')
            rpes = request.form.getlist('rpe[]')
            item_notes = request.form.getlist('item_notes[]')

            for i in range(len(exercise_names)):
                name = exercise_names[i].strip()
                if not name:
                    continue
                set_num = int(set_numbers[i]) if i < len(set_numbers) and set_numbers[i] else 1
                w = float(weights[i]) if i < len(weights) and weights[i] else 0.0
                r = int(reps[i]) if i < len(reps) and reps[i] else 0
                set_rpe = float(rpes[i]) if i < len(rpes) and rpes[i] else None
                note = item_notes[i] if i < len(item_notes) else ''

                item = WorkoutLogItem(
                    log_id=workout_log.id,
                    exercise_name=name,
                    set_number=set_num,
                    weight_kg=w,
                    reps_completed=r,
                    rpe=set_rpe,
                    notes=note
                )
                db.session.add(item)

            db.session.commit()

            # Trigger adaptive coaching analysis
            CoachingEngine.generate_recommendations(current_user.id)

            flash('Workout session logged successfully! Check adaptive coaching recommendations in your dashboard.', 'success')
            return redirect(url_for('workout.workout_history'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error logging workout: {str(e)}', 'danger')

    active_plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    return render_template('workout/log.html', plan=active_plan, today=datetime.utcnow().strftime('%Y-%m-%d'))


@workout_bp.route('/history')
@login_required
def workout_history():
    logs = WorkoutLog.query.filter_by(user_id=current_user.id).order_by(WorkoutLog.date.desc()).all()
    prs = CoachingEngine.get_user_prs(current_user.id)
    return render_template('workout/workout_history.html', logs=logs, prs=prs)


@workout_bp.route('/log/<int:log_id>/delete', methods=['POST'])
@login_required
def delete_log(log_id):
    log = WorkoutLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    db.session.delete(log)
    db.session.commit()
    flash('Workout log deleted.', 'info')
    return redirect(url_for('workout.workout_history'))
