from datetime import datetime, timezone, date
from app import db

def utc_now():
    return datetime.now(timezone.utc)

def today_date():
    return datetime.now(timezone.utc).date()

class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    split_type = db.Column(db.String(50), nullable=False)  # full_body, upper_lower, ppl, home_minimal, return_to_training
    duration_weeks = db.Column(db.Integer, default=8)
    goal = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    progression_model = db.Column(db.String(120), default="Double progression (reps first, then load)")
    recovery_guidelines = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationship to days
    days = db.relationship('WorkoutDay', backref='plan', cascade='all, delete-orphan', order_by='WorkoutDay.day_number')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'split_type': self.split_type,
            'duration_weeks': self.duration_weeks,
            'goal': self.goal,
            'description': self.description,
            'progression_model': self.progression_model,
            'recovery_guidelines': self.recovery_guidelines,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'days': [day.to_dict() for day in self.days]
        }


class WorkoutDay(db.Model):
    __tablename__ = 'workout_days'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=False, index=True)
    day_number = db.Column(db.Integer, nullable=False)  # 1 to 7
    day_name = db.Column(db.String(80), nullable=False)  # e.g. "Day 1 - Push Focus"
    focus = db.Column(db.String(120), nullable=False)    # e.g. "Chest, Shoulders & Triceps"
    warm_up = db.Column(db.Text, nullable=True)
    cool_down = db.Column(db.Text, nullable=True)
    estimated_duration_min = db.Column(db.Integer, default=45)
    is_rest_day = db.Column(db.Boolean, default=False)

    exercises = db.relationship('WorkoutExercise', backref='day', cascade='all, delete-orphan', order_by='WorkoutExercise.order_index')

    def to_dict(self):
        return {
            'id': self.id,
            'day_number': self.day_number,
            'day_name': self.day_name,
            'focus': self.focus,
            'warm_up': self.warm_up,
            'cool_down': self.cool_down,
            'estimated_duration_min': self.estimated_duration_min,
            'is_rest_day': self.is_rest_day,
            'exercises': [ex.to_dict() for ex in self.exercises]
        }


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey('workout_days.id'), nullable=False, index=True)
    exercise_name = db.Column(db.String(120), nullable=False)
    target_muscle = db.Column(db.String(60), nullable=False)
    equipment = db.Column(db.String(60), nullable=False)
    sets = db.Column(db.Integer, default=3)
    reps = db.Column(db.String(40), default="8-12")
    rest_seconds = db.Column(db.Integer, default=90)
    rpe_target = db.Column(db.String(30), default="7-8 (1-2 RIR)")
    technique_cue = db.Column(db.Text, nullable=True)
    substitutions = db.Column(db.JSON, default=list)  # list of alternate exercise names
    order_index = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'exercise_name': self.exercise_name,
            'target_muscle': self.target_muscle,
            'equipment': self.equipment,
            'sets': self.sets,
            'reps': self.reps,
            'rest_seconds': self.rest_seconds,
            'rpe_target': self.rpe_target,
            'technique_cue': self.technique_cue,
            'substitutions': self.substitutions or [],
            'order_index': self.order_index
        }


class WorkoutLog(db.Model):
    __tablename__ = 'workout_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=today_date)
    session_name = db.Column(db.String(120), default="Workout Session")
    duration_minutes = db.Column(db.Integer, default=45)
    perceived_exertion = db.Column(db.Integer, default=7)  # 1-10 RPE
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    items = db.relationship('WorkoutLogItem', backref='log', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else '',
            'session_name': self.session_name,
            'duration_minutes': self.duration_minutes,
            'perceived_exertion': self.perceived_exertion,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items]
        }


class WorkoutLogItem(db.Model):
    __tablename__ = 'workout_log_items'

    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.Integer, db.ForeignKey('workout_logs.id'), nullable=False, index=True)
    exercise_name = db.Column(db.String(120), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, default=0.0)
    reps_completed = db.Column(db.Integer, default=0)
    rpe = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'exercise_name': self.exercise_name,
            'set_number': self.set_number,
            'weight_kg': self.weight_kg,
            'reps_completed': self.reps_completed,
            'rpe': self.rpe,
            'notes': self.notes
        }
