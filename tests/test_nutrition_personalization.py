import pytest
from app import db
from app.models.user import User, UserProfile
from app.models.nutrition import FoodItem, MealPlan, MealPlanItem
from app.services.nutrition_engine import NutritionEngine

def test_nutrition_calculations_and_safety(app):
    """Point 10: Mifflin-St Jeor BMR math, TDEE, macronutrient targets, and underage safety."""
    with app.app_context():
        # Standard Adult Male (70kg, 175cm, 25yo, sedentary)
        # BMR = (10 * 70) + (6.25 * 175) - (5 * 25) + 5 = 700 + 1093.75 - 125 + 5 = 1673.75
        bmr_calc = NutritionEngine.calculate_bmr(70.0, 175.0, 25, 'Male')
        assert round(bmr_calc) == 1674

        profile_male = UserProfile(
            age=25,
            gender='Male',
            height_cm=175.0,
            weight_kg=70.0,
            activity_level='sedentary',
            primary_goal='fat_loss'
        )
        targets = NutritionEngine.calculate_targets(profile_male)
        assert targets['target_calories'] < 1674 * 1.2  # deficit applied
        assert targets['target_protein'] >= 70.0 * 1.8  # elevated protein in fat loss deficit

        # Minor Safety Check (< 18 yo)
        profile_minor = UserProfile(
            age=16,
            gender='Female',
            height_cm=160.0,
            weight_kg=52.0,
            activity_level='moderately_active',
            primary_goal='fat_loss'
        )
        minor_targets = NutritionEngine.calculate_targets(profile_minor)
        assert "SAFETY NOTICE" in minor_targets['calculation_notes']
        assert "under 18 years of age" in minor_targets['calculation_notes']

def test_dietary_restrictions(app):
    """Point 8: Dietary patterns (Vegetarian, Vegan, Eggetarian, Non-Vegetarian)."""
    with app.app_context():
        # Vegan Profile: Absolutely no dairy or eggs
        profile_vegan = UserProfile(
            age=22,
            gender='Male',
            height_cm=172.0,
            weight_kg=65.0,
            diet_type='vegan',
            cooking_facility='full_kitchen',
            meal_frequency=3
        )
        vegan_plan = NutritionEngine.generate_meal_plan(1, profile_vegan)
        for item in vegan_plan.items:
            food = FoodItem.query.filter_by(name=item.food_name).first()
            if food:
                assert food.diet_type.lower() == 'vegan'
                assert food.contains_dairy is False
                assert food.contains_egg is False

        # Eggetarian Profile: May contain eggs and veg, but no meat
        profile_egg = UserProfile(
            age=22,
            gender='Male',
            height_cm=172.0,
            weight_kg=65.0,
            diet_type='eggetarian',
            cooking_facility='hostel_mess',
            meal_frequency=3
        )
        egg_plan = NutritionEngine.generate_meal_plan(1, profile_egg)
        for item in egg_plan.items:
            food = FoodItem.query.filter_by(name=item.food_name).first()
            if food:
                assert food.diet_type.lower() in ['vegan', 'vegetarian', 'eggetarian']
                assert "Chicken" not in food.name
                assert "Fish" not in food.name

def test_food_allergies_exclusion(app):
    """Point 9: Strict exclusion of allergen foods."""
    with app.app_context():
        # Dairy and Peanut allergy
        profile_allergic = UserProfile(
            age=23,
            gender='Female',
            height_cm=168.0,
            weight_kg=60.0,
            diet_type='vegetarian',
            allergies=['peanuts', 'dairy'],
            cooking_facility='full_kitchen'
        )
        plan = NutritionEngine.generate_meal_plan(1, profile_allergic)
        for item in plan.items:
            food = FoodItem.query.filter_by(name=item.food_name).first()
            if food:
                assert food.contains_peanuts is False
                assert food.contains_dairy is False
                assert "Paneer" not in food.name
                assert "Milk" not in food.name
                assert "Peanut" not in food.name

def test_meal_portion_editing_and_recalculations(client, app, registered_user):
    """Point 11: Editing meal portion accurately recalculates nutritional totals."""
    client.post('/auth/login', data={'login_id': 'testuser', 'password': 'password123'})

    # Generate initial plan
    client.get('/nutrition/plan')

    with app.app_context():
        plan = MealPlan.query.filter_by(user_id=registered_user, is_active=True).first()
        item = plan.items[0]
        item_id = item.id
        original_cals = item.calories
        original_portion = item.portion_grams

    # Double the portion size via POST
    new_portion = original_portion * 2
    res = client.post(f'/nutrition/plan/item/{item_id}/edit', data={
        'portion_grams': str(new_portion)
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        updated_item = MealPlanItem.query.get(item_id)
        assert updated_item.portion_grams == new_portion
        # Calories should approximately double
        assert abs(updated_item.calories - (original_cals * 2)) <= 1.0
