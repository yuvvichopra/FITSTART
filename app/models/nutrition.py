from datetime import datetime, timezone, date
from app import db

def utc_now():
    return datetime.now(timezone.utc)

def today_date():
    return datetime.now(timezone.utc).date()

class FoodItem(db.Model):
    __tablename__ = 'food_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False)  # Lentils & Dals, Dairy & Paneer, Grains, Vegetables, Fruits, Poultry & Eggs, Nuts & Seeds
    region = db.Column(db.String(50), default="Indian Common")  # North Indian, South Indian, Indian Common, Global
    diet_type = db.Column(db.String(50), default="Vegetarian")  # Vegetarian, Vegan, Eggetarian, Non-Vegetarian
    calories_per_100g = db.Column(db.Float, nullable=False)
    protein_per_100g = db.Column(db.Float, nullable=False)
    carbs_per_100g = db.Column(db.Float, nullable=False)
    fat_per_100g = db.Column(db.Float, nullable=False)
    fiber_per_100g = db.Column(db.Float, default=0.0)
    serving_size_unit = db.Column(db.String(60), default="100g")
    default_serving_grams = db.Column(db.Float, default=100.0)
    
    # Practical filters
    is_hostel_friendly = db.Column(db.Boolean, default=False)
    is_budget_friendly = db.Column(db.Boolean, default=True)
    
    # Allergens
    contains_peanuts = db.Column(db.Boolean, default=False)
    contains_tree_nuts = db.Column(db.Boolean, default=False)
    contains_dairy = db.Column(db.Boolean, default=False)
    contains_gluten = db.Column(db.Boolean, default=False)
    contains_soy = db.Column(db.Boolean, default=False)
    contains_egg = db.Column(db.Boolean, default=False)
    contains_shellfish = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'region': self.region,
            'diet_type': self.diet_type,
            'calories_per_100g': self.calories_per_100g,
            'protein_per_100g': self.protein_per_100g,
            'carbs_per_100g': self.carbs_per_100g,
            'fat_per_100g': self.fat_per_100g,
            'fiber_per_100g': self.fiber_per_100g,
            'serving_size_unit': self.serving_size_unit,
            'default_serving_grams': self.default_serving_grams,
            'is_hostel_friendly': self.is_hostel_friendly,
            'is_budget_friendly': self.is_budget_friendly,
            'allergens': {
                'peanuts': self.contains_peanuts,
                'tree_nuts': self.contains_tree_nuts,
                'dairy': self.contains_dairy,
                'gluten': self.contains_gluten,
                'soy': self.contains_soy,
                'egg': self.contains_egg,
                'shellfish': self.contains_shellfish
            }
        }


class MealPlan(db.Model):
    __tablename__ = 'meal_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(120), default="Personalized Daily Nutrition Plan")
    target_calories = db.Column(db.Float, nullable=False)
    target_protein = db.Column(db.Float, nullable=False)
    target_carbs = db.Column(db.Float, nullable=False)
    target_fat = db.Column(db.Float, nullable=False)
    target_fiber = db.Column(db.Float, default=30.0)
    calculation_notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    items = db.relationship('MealPlanItem', backref='meal_plan', cascade='all, delete-orphan', order_by='MealPlanItem.order_index')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'target_calories': round(self.target_calories, 1),
            'target_protein': round(self.target_protein, 1),
            'target_carbs': round(self.target_carbs, 1),
            'target_fat': round(self.target_fat, 1),
            'target_fiber': round(self.target_fiber, 1),
            'calculation_notes': self.calculation_notes,
            'is_active': self.is_active,
            'version': self.version,
            'items': [item.to_dict() for item in self.items]
        }


class MealPlanItem(db.Model):
    __tablename__ = 'meal_plan_items'

    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False, index=True)
    meal_type = db.Column(db.String(30), nullable=False)  # Breakfast, Lunch, Evening Snack, Dinner
    food_id = db.Column(db.Integer, db.ForeignKey('food_items.id'), nullable=True)
    food_name = db.Column(db.String(120), nullable=False)
    portion_grams = db.Column(db.Float, nullable=False)
    portion_description = db.Column(db.String(100), nullable=True)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    fiber = db.Column(db.Float, default=0.0)
    order_index = db.Column(db.Integer, default=0)

    food = db.relationship('FoodItem')

    def to_dict(self):
        return {
            'id': self.id,
            'meal_type': self.meal_type,
            'food_id': self.food_id,
            'food_name': self.food_name,
            'portion_grams': round(self.portion_grams, 1),
            'portion_description': self.portion_description,
            'calories': round(self.calories, 1),
            'protein': round(self.protein, 1),
            'carbs': round(self.carbs, 1),
            'fat': round(self.fat, 1),
            'fiber': round(self.fiber, 1),
            'order_index': self.order_index
        }


class DailyNutritionLog(db.Model):
    __tablename__ = 'daily_nutrition_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=today_date, index=True)
    meal_type = db.Column(db.String(30), nullable=False)
    food_name = db.Column(db.String(120), nullable=False)
    portion_grams = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    fiber = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else '',
            'meal_type': self.meal_type,
            'food_name': self.food_name,
            'portion_grams': round(self.portion_grams, 1),
            'calories': round(self.calories, 1),
            'protein': round(self.protein, 1),
            'carbs': round(self.carbs, 1),
            'fat': round(self.fat, 1),
            'fiber': round(self.fiber, 1)
        }
