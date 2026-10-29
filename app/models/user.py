from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

def utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    workout_plans = db.relationship('WorkoutPlan', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    workout_logs = db.relationship('WorkoutLog', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    meal_plans = db.relationship('MealPlan', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    daily_nutrition_logs = db.relationship('DailyNutritionLog', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    daily_habit_logs = db.relationship('DailyHabitLog', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    recommendations = db.relationship('CoachingRecommendation', backref='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Personal information
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(30), nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    unit_system = db.Column(db.String(20), default='metric')  # 'metric' or 'imperial'
    region = db.Column(db.String(50), default='North Indian')
    activity_level = db.Column(db.String(50), default='moderately_active')

    # Experience
    experience_level = db.Column(db.String(50), default='beginner')
    training_history = db.Column(db.Text, nullable=True)
    previous_structured_training = db.Column(db.Boolean, default=False)
    exercise_confidence = db.Column(db.Integer, default=3)  # 1 to 5
    current_training_frequency = db.Column(db.Integer, default=0)
    preferred_session_length = db.Column(db.Integer, default=45)  # minutes

    # Goals
    primary_goal = db.Column(db.String(50), default='general_fitness')
    secondary_goals = db.Column(db.JSON, default=list)  # list of strings

    # Equipment
    equipment_setting = db.Column(db.String(50), default='commercial_gym')
    available_equipment = db.Column(db.JSON, default=list)

    # Schedule
    training_days_count = db.Column(db.Integer, default=3)
    preferred_days = db.Column(db.JSON, default=list)
    preferred_time = db.Column(db.String(30), default='morning')
    cardio_preference = db.Column(db.String(50), default='walking')
    schedule_constraints = db.Column(db.String(255), nullable=True)

    # Diet & Nutrition
    diet_type = db.Column(db.String(50), default='vegetarian')
    allergies = db.Column(db.JSON, default=list)
    food_intolerances = db.Column(db.String(255), nullable=True)
    food_dislikes = db.Column(db.JSON, default=list)
    budget_level = db.Column(db.String(30), default='moderate')
    meal_frequency = db.Column(db.Integer, default=3)
    cooking_facility = db.Column(db.String(50), default='hostel_mess')
    preferred_protein_sources = db.Column(db.JSON, default=list)
    meal_timing = db.Column(db.String(50), default='standard')

    # Recovery and Safety
    sleep_hours = db.Column(db.Float, default=7.0)
    daily_step_target = db.Column(db.Integer, default=8000)
    recovery_preferences = db.Column(db.JSON, default=list)
    pain_movements = db.Column(db.JSON, default=list)
    physical_restrictions = db.Column(db.Text, nullable=True)
    medical_conditions = db.Column(db.Text, nullable=True)

    # Additional preferences
    priority_muscle_groups = db.Column(db.JSON, default=list)
    favourite_exercises = db.Column(db.JSON, default=list)
    disliked_exercises = db.Column(db.JSON, default=list)
    coaching_style = db.Column(db.String(50), default='encouraging')
    desired_difficulty = db.Column(db.String(30), default='moderate')

    onboarding_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'age': self.age,
            'gender': self.gender,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'unit_system': self.unit_system,
            'region': self.region,
            'activity_level': self.activity_level,
            'experience_level': self.experience_level,
            'primary_goal': self.primary_goal,
            'secondary_goals': self.secondary_goals or [],
            'equipment_setting': self.equipment_setting,
            'available_equipment': self.available_equipment or [],
            'training_days_count': self.training_days_count,
            'preferred_days': self.preferred_days or [],
            'diet_type': self.diet_type,
            'allergies': self.allergies or [],
            'cooking_facility': self.cooking_facility,
            'budget_level': self.budget_level,
            'sleep_hours': self.sleep_hours,
            'daily_step_target': self.daily_step_target,
            'pain_movements': self.pain_movements or [],
            'medical_conditions': self.medical_conditions,
            'coaching_style': self.coaching_style,
            'onboarding_completed': self.onboarding_completed
        }
