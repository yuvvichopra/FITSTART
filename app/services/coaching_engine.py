from datetime import datetime, timedelta
from app import db
from app.models.workout import WorkoutLog, WorkoutLogItem
from app.models.habit import DailyHabitLog, CoachingRecommendation

class CoachingEngine:
    """Adaptive coaching recommendation engine based on logged performance and habits."""

    @staticmethod
    def calculate_estimated_1rm(weight_kg, reps):
        """Calculates estimated 1RM using the validated Epley formula."""
        if reps <= 0 or weight_kg <= 0:
            return 0.0
        if reps == 1:
            return float(weight_kg)
        return round(float(weight_kg) * (1.0 + float(reps) / 30.0), 1)

    @classmethod
    def get_user_prs(cls, user_id):
        """Calculates all-time personal records for the user across exercises."""
        logs = WorkoutLog.query.filter_by(user_id=user_id).all()
        prs = {}

        for log in logs:
            for item in log.items:
                ex_name = item.exercise_name
                weight = item.weight_kg or 0.0
                reps = item.reps_completed or 0
                est_1rm = cls.calculate_estimated_1rm(weight, reps)

                if ex_name not in prs or est_1rm > prs[ex_name]['est_1rm']:
                    prs[ex_name] = {
                        'exercise_name': ex_name,
                        'weight_kg': weight,
                        'reps': reps,
                        'est_1rm': est_1rm,
                        'date': log.date.strftime('%Y-%m-%d') if log.date else ''
                    }

        return prs

    @classmethod
    def generate_recommendations(cls, user_id):
        """
        Analyzes recent logs and generates transparent, adaptive coaching suggestions.
        Never increases load if pain or poor recovery is reported.
        """
        recent_logs = WorkoutLog.query.filter_by(user_id=user_id).order_by(WorkoutLog.date.desc()).limit(5).all()
        recent_habits = DailyHabitLog.query.filter_by(user_id=user_id).order_by(DailyHabitLog.date.desc()).limit(7).all()

        recommendations = []

        # Check recovery habits first
        poor_sleep = False
        sore_or_pain = False
        avg_sleep = 0.0

        if recent_habits:
            sleep_vals = [h.sleep_hours for h in recent_habits if h.sleep_hours and h.sleep_hours > 0]
            if sleep_vals:
                avg_sleep = sum(sleep_vals) / len(sleep_vals)
                if avg_sleep < 6.0:
                    poor_sleep = True

            recent_recovery = [h.recovery_feeling for h in recent_habits if h.recovery_feeling]
            if any(r in ['fatigued', 'sore', 'pain'] for r in recent_recovery):
                sore_or_pain = True

        # Safety / Recovery Recommendation
        if sore_or_pain or poor_sleep:
            rationale_parts = []
            if poor_sleep:
                rationale_parts.append(f"Recent average sleep is {round(avg_sleep, 1)} hours (< 6h threshold).")
            if sore_or_pain:
                rationale_parts.append("You noted muscle soreness or fatigue in your habit logs.")

            rec = CoachingRecommendation(
                user_id=user_id,
                category="recovery",
                title="Adaptive Recovery Alert: Prioritize Sleep and Active Rest",
                recommendation_text="Do not increase training weights in your upcoming session. Maintain current weights or reduce total working sets by 20% to avoid overuse strain.",
                rationale=" ".join(rationale_parts) + " NSCA & ACSM guidelines emphasize that tissue repair occurs primarily during slow-wave sleep; pushing loads in fatigued states elevates injury risk.",
                status="pending"
            )
            recommendations.append(rec)

        # Workout Progressive Overload Analysis
        if recent_logs:
            latest_session = recent_logs[0]
            # Analyze each exercise in the latest session
            ex_items = {}
            for item in latest_session.items:
                ex_items.setdefault(item.exercise_name, []).append(item)

            for ex_name, sets in ex_items.items():
                if not sets:
                    continue
                # Check if all sets completed clean reps with low/moderate RPE
                all_high_reps = all((s.reps_completed or 0) >= 10 for s in sets)
                low_rpe = all((s.rpe or 7) <= 8 for s in sets)
                current_weight = sets[0].weight_kg or 0.0

                if all_high_reps and low_rpe and not sore_or_pain:
                    suggested_weight = round(current_weight + (2.5 if current_weight > 0 else 0), 1)
                    rec = CoachingRecommendation(
                        user_id=user_id,
                        category="workout",
                        title=f"Progressive Overload: Ready to advance on {ex_name}",
                        recommendation_text=f"You successfully completed your target sets of {sets[0].reps_completed} reps at {current_weight}kg with controlled RPE. Try advancing to {suggested_weight}kg next session.",
                        rationale=f"Linear double progression rule: hitting top reps across all working sets with RPE <= 8 signals neuromuscular adaptation.",
                        status="pending"
                    )
                    recommendations.append(rec)
                    break # Suggest one key exercise progression per session to avoid overwhelming user

                elif any((s.rpe or 7) >= 9 for s in sets):
                    rec = CoachingRecommendation(
                        user_id=user_id,
                        category="workout",
                        title=f"Consolidate Form: Hold weight on {ex_name}",
                        recommendation_text=f"Perceived exertion was elevated (RPE >= 9) on {ex_name}. Keep the weight at {current_weight}kg for your next session and focus on crisp technique.",
                        rationale="Consolidating form at a given load before adding weight prevents technical breakdown and joint strain.",
                        status="pending"
                    )
                    recommendations.append(rec)
                    break

        # Save to DB if not duplicates
        saved_recs = []
        for r in recommendations:
            existing = CoachingRecommendation.query.filter_by(
                user_id=user_id,
                title=r.title,
                status="pending"
            ).first()
            if not existing:
                db.session.add(r)
                saved_recs.append(r)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        return saved_recs
