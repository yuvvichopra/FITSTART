import pytest
from app import create_app, db
from app.models.user import User, UserProfile
from app.services.seed_data import seed_initial_data

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        seed_initial_data()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def registered_user(app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(
            user_id=user.id,
            age=22,
            gender="Male",
            height_cm=175.0,
            weight_kg=70.0,
            unit_system="metric",
            region="North Indian",
            activity_level="moderately_active",
            experience_level="beginner",
            primary_goal="muscle_gain",
            equipment_setting="commercial_gym",
            training_days_count=3,
            diet_type="vegetarian",
            cooking_facility="hostel_mess",
            sleep_hours=7.5,
            onboarding_completed=True
        )
        db.session.add(profile)
        db.session.commit()
        return user.id

@pytest.fixture
def second_user(app):
    with app.app_context():
        user = User(username="otheruser", email="other@example.com")
        user.set_password("password456")
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(
            user_id=user.id,
            age=25,
            gender="Female",
            height_cm=165.0,
            weight_kg=58.0,
            unit_system="metric",
            region="South Indian",
            activity_level="lightly_active",
            experience_level="consistent",
            primary_goal="fat_loss",
            equipment_setting="home_gym",
            training_days_count=4,
            diet_type="vegan",
            cooking_facility="full_kitchen",
            sleep_hours=8.0,
            onboarding_completed=True
        )
        db.session.add(profile)
        db.session.commit()
        return user.id
