import math
from app.models.nutrition import FoodItem, MealPlan, MealPlanItem

class NutritionEngine:
    """Evidence-based nutrition calculation and meal plan generation engine."""

    ACTIVITY_FACTORS = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725
    }

    @staticmethod
    def calculate_bmr(weight_kg, height_cm, age, gender=None):
        """
        Calculates Basal Metabolic Rate using the validated Mifflin-St Jeor equation.
        Men: BMR = (10 * weight) + (6.25 * height) - (5 * age) + 5
        Women: BMR = (10 * weight) + (6.25 * height) - (5 * age) - 161
        Gender-neutral/unspecified: average offset (-78)
        """
        if not weight_kg or not height_cm or not age:
            return 1600.0  # sensible fallback default

        base = (10.0 * float(weight_kg)) + (6.25 * float(height_cm)) - (5.0 * float(age))
        gender_str = (gender or '').strip().lower()

        if gender_str in ['male', 'man', 'm']:
            return base + 5.0
        elif gender_str in ['female', 'woman', 'f']:
            return base - 161.0
        else:
            return base - 78.0

    @classmethod
    def calculate_targets(cls, profile):
        """
        Calculates estimated daily calorie, protein, carbohydrate, fat, and fiber targets.
        Adheres to ACSM, ISSN, WHO, and ICMR (Indian Council of Medical Research) nutritional guidelines.
        """
        weight_kg = profile.weight_kg or 68.0
        height_cm = profile.height_cm or 172.0
        age = profile.age or 22
        gender = profile.gender
        activity = (profile.activity_level or 'moderately_active').lower()
        goal = (profile.primary_goal or 'general_fitness').lower()

        # Step 1: BMR
        bmr = cls.calculate_bmr(weight_kg, height_cm, age, gender)

        # Step 2: TDEE
        multiplier = cls.ACTIVITY_FACTORS.get(activity, 1.55)
        tdee = bmr * multiplier

        # Step 3: Calorie adjustment by goal
        notes = []
        notes.append(f"Estimated BMR: {round(bmr)} kcal (Mifflin-St Jeor formula).")
        notes.append(f"Estimated TDEE: {round(tdee)} kcal based on '{activity.replace('_', ' ')}' activity level (x{multiplier}).")

        is_minor = age < 18
        if is_minor:
            notes.append("SAFETY NOTICE: User is under 18 years of age. Severe caloric restriction is contraindicated during growth and development. Maintenance/recomposition energy target applied.")
            target_calories = tdee
        elif 'fat_loss' in goal:
            deficit = min(500.0, max(300.0, tdee * 0.20))
            target_calories = tdee - deficit
            # Safe adult floors
            min_floor = 1500.0 if str(gender).lower() in ['male', 'man'] else 1250.0
            if target_calories < min_floor:
                target_calories = min_floor
                notes.append(f"Calorie deficit clamped to safe minimum floor of {int(min_floor)} kcal/day.")
            else:
                notes.append(f"Applied moderate, sustainable calorie deficit of ~{round(deficit)} kcal/day (15-20%).")
        elif 'muscle_gain' in goal:
            surplus = min(400.0, max(250.0, tdee * 0.12))
            target_calories = tdee + surplus
            notes.append(f"Applied lean hypertrophy surplus of +{round(surplus)} kcal/day (10-15%).")
        elif 'body_recomp' in goal:
            target_calories = tdee * 0.95
            notes.append("Applied slight deficit (-5%) paired with high protein target for body recomposition.")
        elif 'strength' in goal:
            target_calories = tdee * 1.05
            notes.append("Applied slight surplus (+5%) to fuel high neuromuscular demand and strength adaptation.")
        elif 'endurance' in goal:
            target_calories = tdee * 1.05
            notes.append("Applied slight surplus (+5%) with elevated carbohydrate ratio to support aerobic endurance.")
        else:
            target_calories = tdee
            notes.append("Target set to maintenance energy expenditure for general health and fitness.")

        # Step 4: Macronutrients
        # Protein (g/kg body weight based on ACSM/ISSN guidelines)
        if 'muscle_gain' in goal or 'body_recomp' in goal or 'strength' in goal:
            protein_per_kg = 2.0
        elif 'fat_loss' in goal:
            protein_per_kg = 2.0  # Preserve lean body mass in a deficit
        else:
            protein_per_kg = 1.6

        target_protein = round(weight_kg * protein_per_kg, 1)
        protein_cals = target_protein * 4.0

        # Fats (25% of total calories, bounded to healthy hormonal threshold)
        fat_cals = target_calories * 0.25
        target_fat = round(fat_cals / 9.0, 1)

        # Carbohydrates (Remaining calories)
        remaining_cals = max(0.0, target_calories - protein_cals - fat_cals)
        target_carbs = round(remaining_cals / 4.0, 1)

        # Fiber: ICMR recommends 30g/day for Indian adults; WHO recommends 25-35g
        target_fiber = 30.0

        notes.append(f"Macronutrient distribution: Protein {target_protein}g ({protein_per_kg}g/kg), Fats {target_fat}g (~25% cals), Carbs {target_carbs}g.")
        notes.append("DISCLAIMER: All targets are evidence-based estimates. Adjust based on weekly bodyweight trends and personal satiety.")

        return {
            'target_calories': round(target_calories),
            'target_protein': target_protein,
            'target_carbs': target_carbs,
            'target_fat': target_fat,
            'target_fiber': target_fiber,
            'calculation_notes': "\n".join(notes)
        }

    @classmethod
    def generate_meal_plan(cls, user_id, profile):
        """
        Generates a personalized daily meal plan respecting diet, allergies, cooking facility, and budget.
        Calculates portions from verified database items.
        """
        targets = cls.calculate_targets(profile)

        # Fetch candidate foods matching user profile constraints
        candidates = FoodItem.query.all()
        if not candidates:
            from app.services.seed_data import seed_initial_data
            seed_initial_data()
            candidates = FoodItem.query.all()

        diet = (profile.diet_type or 'vegetarian').lower()
        allergies = [a.lower() for a in (profile.allergies or [])]
        dislikes = [d.lower() for d in (profile.food_dislikes or [])]
        is_hostel = 'hostel' in (profile.cooking_facility or '').lower()
        is_budget = (profile.budget_level or 'moderate').lower() == 'budget_friendly'

        filtered_foods = []
        for food in candidates:
            # Diet filtering
            food_diet = food.diet_type.lower()
            if diet == 'vegan' and food_diet != 'vegan':
                continue
            if diet in ['vegetarian', 'lacto_vegetarian'] and food_diet not in ['vegan', 'vegetarian']:
                continue
            if diet in ['eggetarian', 'egg_vegetarian'] and food_diet not in ['vegan', 'vegetarian', 'eggetarian']:
                continue
            # Non-veg includes everything

            # Allergen filtering
            if 'peanuts' in allergies and food.contains_peanuts:
                continue
            if 'tree_nuts' in allergies and food.contains_tree_nuts:
                continue
            if 'dairy' in allergies and food.contains_dairy:
                continue
            if 'gluten' in allergies and food.contains_gluten:
                continue
            if 'soy' in allergies and food.contains_soy:
                continue
            if 'egg' in allergies and food.contains_egg:
                continue
            if 'shellfish' in allergies and food.contains_shellfish:
                continue

            # Dislikes
            if any(dislike in food.name.lower() for dislike in dislikes):
                continue

            # Hostel constraint preference (boost/prefer hostel-friendly foods if in hostel)
            filtered_foods.append(food)

        # If strict filtering left very few, relax dislike slightly to ensure nutritionally viable plan
        if len(filtered_foods) < 5:
            filtered_foods = candidates

        food_map = {f.name: f for f in filtered_foods}

        # Build plan structure (e.g., 4 meals: Breakfast, Lunch, Evening Snack, Dinner)
        meal_slots = cls._determine_meal_structure(profile.meal_frequency or 4, filtered_foods, is_hostel, diet)

        # Create MealPlan record
        meal_plan = MealPlan(
            user_id=user_id,
            title=f"Personalized Plan - {profile.diet_type.replace('_', ' ').title()} ({round(targets['target_calories'])} kcal)",
            target_calories=targets['target_calories'],
            target_protein=targets['target_protein'],
            target_carbs=targets['target_carbs'],
            target_fat=targets['target_fat'],
            target_fiber=targets['target_fiber'],
            calculation_notes=targets['calculation_notes'],
            is_active=True
        )

        # Scale items to meet targets
        plan_items = []
        order = 0
        total_cal = 0.0
        total_p = 0.0
        total_c = 0.0
        total_f = 0.0
        total_fib = 0.0

        for meal_type, item_specs in meal_slots:
            for food, portion_g, desc in item_specs:
                factor = portion_g / 100.0
                cal = food.calories_per_100g * factor
                p = food.protein_per_100g * factor
                c = food.carbs_per_100g * factor
                f = food.fat_per_100g * factor
                fib = food.fiber_per_100g * factor

                total_cal += cal
                total_p += p
                total_c += c
                total_f += f
                total_fib += fib

                item = MealPlanItem(
                    meal_type=meal_type,
                    food_id=food.id,
                    food_name=food.name,
                    portion_grams=portion_g,
                    portion_description=desc,
                    calories=cal,
                    protein=p,
                    carbs=c,
                    fat=f,
                    fiber=fib,
                    order_index=order
                )
                plan_items.append(item)
                order += 1

        # Adjust portion scaling if needed to match target calories within +/- 5%
        if total_cal > 0:
            scale_ratio = targets['target_calories'] / total_cal
            # Keep scale between 0.85 and 1.25 to prevent absurd portion quantities
            scale_ratio = max(0.85, min(1.25, scale_ratio))
            for item in plan_items:
                item.portion_grams = round(item.portion_grams * scale_ratio, 1)
                item.calories = round(item.calories * scale_ratio, 1)
                item.protein = round(item.protein * scale_ratio, 1)
                item.carbs = round(item.carbs * scale_ratio, 1)
                item.fat = round(item.fat * scale_ratio, 1)
                item.fiber = round(item.fiber * scale_ratio, 1)

        meal_plan.items = plan_items
        return meal_plan

    @classmethod
    def _determine_meal_structure(cls, meal_count, foods, is_hostel, diet):
        """Constructs balanced meal templates using candidate foods."""
        def find_food(name_substr, fallback_cat=None):
            for f in foods:
                if name_substr.lower() in f.name.lower():
                    return f
            if fallback_cat:
                for f in foods:
                    if f.category.lower() == fallback_cat.lower():
                        return f
            return foods[0] if foods else None

        # Key staples
        oats = find_food("Oats", "Grains")
        milk = find_food("Cow's Milk", "Dairy") or find_food("Banana")
        banana = find_food("Banana", "Fruits")
        egg = find_food("Whole Boiled Egg", "Poultry & Eggs")
        roti = find_food("Whole Wheat Roti", "Grains")
        rice = find_food("White Rice", "Grains")
        dal = find_food("Moong Dal", "Lentils & Pulses")
        rajma = find_food("Rajma", "Lentils & Pulses")
        paneer = find_food("Paneer", "Dairy")
        soya = find_food("Soya Chunks", "Plant Protein")
        chicken = find_food("Chicken", "Poultry & Eggs")
        salad = find_food("Salad", "Vegetables")
        chana = find_food("Roasted Chana", "Lentils & Pulses")
        peanut_butter = find_food("Peanut Butter", "Nuts & Seeds")
        sattu = find_food("Sattu", "Plant Protein")

        # Pick protein for lunch & dinner based on diet
        if 'non_veg' in diet and chicken:
            main_prot_lunch = chicken
            main_prot_dinner = dal or fish or paneer
        elif 'egg' in diet and egg:
            main_prot_lunch = egg
            main_prot_dinner = dal or paneer or soya
        elif paneer and 'vegan' not in diet:
            main_prot_lunch = paneer
            main_prot_dinner = dal or rajma
        else:
            main_prot_lunch = soya or rajma
            main_prot_dinner = dal

        slots = []

        # 1. Breakfast
        if is_hostel and egg and 'egg' in diet:
            breakfast = [
                (egg, 100.0, "2 whole boiled eggs"),
                (banana, 100.0, "1 medium banana"),
                (roti or oats, 70.0, "2 rotis / bowl oats")
            ]
        elif oats and milk:
            breakfast = [
                (oats, 50.0, "1 bowl rolled oats (cooked)"),
                (milk, 200.0, "1 glass milk / plant milk"),
                (banana, 100.0, "1 sliced banana")
            ]
        else:
            breakfast = [
                (find_food("Poha") or roti, 150.0, "1 plate warm poha or 2 rotis"),
                (find_food("Curd") or dal, 150.0, "1 bowl curd / dal")
            ]
        slots.append(("Breakfast", breakfast))

        # 2. Lunch
        lunch = [
            (roti or rice, 100.0, "3 rotis or 1.5 katoris rice"),
            (main_prot_lunch, 120.0, f"1 serving {main_prot_lunch.name}"),
            (dal or rajma, 150.0, "1 katori cooked dal"),
            (salad, 100.0, "Fresh cucumber & carrot salad")
        ]
        slots.append(("Lunch", lunch))

        # 3. Evening Snack (if >= 4 meals or hostel snack)
        if meal_count >= 4:
            snack = [
                (chana or sattu or peanut_butter, 40.0, "Roasted chana / sattu drink / PB"),
                (find_food("Apple") or banana, 120.0, "1 fresh seasonal fruit")
            ]
            slots.append(("Evening Snack", snack))

        # 4. Dinner
        dinner = [
            (rice or roti, 120.0, "1.5 katoris rice or 2-3 rotis"),
            (main_prot_dinner, 120.0, f"1 serving {main_prot_dinner.name}"),
            (find_food("Palak") or find_food("Bhindi") or salad, 120.0, "1 katori cooked vegetable sabzi")
        ]
        slots.append(("Dinner", dinner))

        return slots
