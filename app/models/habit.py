from datetime import datetime, timezone, date
from app import db

def utc_now():
    return datetime.now(timezone.utc)

def today_date():
    return datetime.now(timezone.utc).date()

class DailyHabitLog(db.Model):
    __tablename__ = 'daily_habit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=today_date, index=True)
    water_ml = db.Column(db.Integer, default=0)
    sleep_hours = db.Column(db.Float, default=0.0)
    sleep_quality = db.Column(db.Integer, default=3)  # 1 to 5 stars
    steps = db.Column(db.Integer, default=0)
    workout_completed = db.Column(db.Boolean, default=False)
    recovery_feeling = db.Column(db.String(50), default="moderate")  # great, good, moderate, fatigued, sore, pain
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Unique constraint per user per date
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uq_user_date_habit'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else '',
            'water_ml': self.water_ml,
            'sleep_hours': self.sleep_hours,
            'sleep_quality': self.sleep_quality,
            'steps': self.steps,
            'workout_completed': self.workout_completed,
            'recovery_feeling': self.recovery_feeling,
            'notes': self.notes
        }


class CoachingRecommendation(db.Model):
    __tablename__ = 'coaching_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=today_date)
    category = db.Column(db.String(50), nullable=False)  # workout, nutrition, recovery, habit
    title = db.Column(db.String(150), nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="pending")  # pending, accepted, rejected, ignored
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else '',
            'category': self.category,
            'title': self.title,
            'recommendation_text': self.recommendation_text,
            'rationale': self.rationale,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }
