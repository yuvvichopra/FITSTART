from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.nutrition import FoodItem, MealPlan, MealPlanItem, DailyNutritionLog
from app.services.nutrition_engine import NutritionEngine

nutrition_bp = Blueprint('nutrition', __name__)

@nutrition_bp.route('/plan')
@login_required
def plan():
    active_plan = MealPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_plan and current_user.profile:
        active_plan = NutritionEngine.generate_meal_plan(current_user.id, current_user.profile)
        db.session.add(active_plan)
        db.session.commit()

    # Calculate actual totals from stored items
    items_by_meal = {}
    plan_totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0, 'fiber': 0.0}

    if active_plan:
        for item in active_plan.items:
            items_by_meal.setdefault(item.meal_type, []).append(item)
            plan_totals['calories'] += item.calories
            plan_totals['protein'] += item.protein
            plan_totals['carbs'] += item.carbs
            plan_totals['fat'] += item.fat
            plan_totals['fiber'] += item.fiber

        # Round totals
        for k in plan_totals:
            plan_totals[k] = round(plan_totals[k], 1)

    return render_template('nutrition/plan.html', plan=active_plan, items_by_meal=items_by_meal, plan_totals=plan_totals)


@nutrition_bp.route('/plan/regenerate', methods=['POST'])
@login_required
def regenerate_plan():
    profile = current_user.profile
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('onboarding.questionnaire'))

    current_plans = MealPlan.query.filter_by(user_id=current_user.id).all()
    for p in current_plans:
        p.is_active = False

    new_version = len(current_plans) + 1
    new_plan = NutritionEngine.generate_meal_plan(current_user.id, profile)
    new_plan.version = new_version
    new_plan.is_active = True
    db.session.add(new_plan)
    db.session.commit()

    flash(f'Fresh personalized nutrition plan (Version {new_version}) generated!', 'success')
    return redirect(url_for('nutrition.plan'))


@nutrition_bp.route('/plan/item/<int:item_id>/edit', methods=['POST'])
@login_required
def edit_plan_item(item_id):
    item = MealPlanItem.query.get_or_404(item_id)
    # Authorization check
    if item.meal_plan.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('nutrition.plan'))

    try:
        new_portion = float(request.form.get('portion_grams', item.portion_grams))
        if new_portion <= 0:
            flash('Portion must be greater than 0 grams.', 'danger')
            return redirect(url_for('nutrition.plan'))

        # Recalculate accurately from stored FoodItem data
        if item.food:
            factor = new_portion / 100.0
            item.portion_grams = new_portion
            item.calories = round(item.food.calories_per_100g * factor, 1)
            item.protein = round(item.food.protein_per_100g * factor, 1)
            item.carbs = round(item.food.carbs_per_100g * factor, 1)
            item.fat = round(item.food.fat_per_100g * factor, 1)
            item.fiber = round(item.food.fiber_per_100g * factor, 1)
            db.session.commit()
            flash(f'Updated {item.food_name} to {new_portion}g. Totals recalculated.', 'success')
        else:
            # Scale proportionally if food item link was decoupled
            scale = new_portion / item.portion_grams
            item.portion_grams = new_portion
            item.calories = round(item.calories * scale, 1)
            item.protein = round(item.protein * scale, 1)
            item.carbs = round(item.carbs * scale, 1)
            item.fat = round(item.fat * scale, 1)
            item.fiber = round(item.fiber * scale, 1)
            db.session.commit()
            flash(f'Updated portion for {item.food_name}.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating portion: {str(e)}', 'danger')

    return redirect(url_for('nutrition.plan'))


@nutrition_bp.route('/plan/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_plan_item(item_id):
    item = MealPlanItem.query.get_or_404(item_id)
    if item.meal_plan.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('nutrition.plan'))

    db.session.delete(item)
    db.session.commit()
    flash(f'Removed {item.food_name} from meal plan.', 'info')
    return redirect(url_for('nutrition.plan'))


@nutrition_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_food():
    selected_date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.utcnow().date()

    if request.method == 'POST':
        try:
            date_input = request.form.get('date', selected_date_str)
            log_date = datetime.strptime(date_input, '%Y-%m-%d').date()
            meal_type = request.form.get('meal_type', 'Lunch')
            food_id = request.form.get('food_id')
            custom_food_name = request.form.get('custom_food_name', '').strip()
            portion_grams = float(request.form.get('portion_grams', 100))

            if food_id and food_id.isdigit():
                food = FoodItem.query.get(int(food_id))
                if food:
                    factor = portion_grams / 100.0
                    log_entry = DailyNutritionLog(
                        user_id=current_user.id,
                        date=log_date,
                        meal_type=meal_type,
                        food_name=food.name,
                        portion_grams=portion_grams,
                        calories=round(food.calories_per_100g * factor, 1),
                        protein=round(food.protein_per_100g * factor, 1),
                        carbs=round(food.carbs_per_100g * factor, 1),
                        fat=round(food.fat_per_100g * factor, 1),
                        fiber=round(food.fiber_per_100g * factor, 1)
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                    flash(f'Logged {food.name} ({portion_grams}g) to {meal_type}.', 'success')
                    return redirect(url_for('nutrition.log_food', date=log_date.strftime('%Y-%m-%d')))

            elif custom_food_name:
                cals = float(request.form.get('custom_calories', 100))
                p = float(request.form.get('custom_protein', 5))
                c = float(request.form.get('custom_carbs', 15))
                f = float(request.form.get('custom_fat', 2))
                fib = float(request.form.get('custom_fiber', 1))

                log_entry = DailyNutritionLog(
                    user_id=current_user.id,
                    date=log_date,
                    meal_type=meal_type,
                    food_name=custom_food_name,
                    portion_grams=portion_grams,
                    calories=cals,
                    protein=p,
                    carbs=c,
                    fat=f,
                    fiber=fib
                )
                db.session.add(log_entry)
                db.session.commit()
                flash(f'Logged custom item "{custom_food_name}" to {meal_type}.', 'success')
                return redirect(url_for('nutrition.log_food', date=log_date.strftime('%Y-%m-%d')))
            else:
                flash('Please select a food from the database or enter a custom food name.', 'warning')

        except Exception as e:
            db.session.rollback()
            flash(f'Error logging food: {str(e)}', 'danger')

    # Fetch logs for selected date
    daily_logs = DailyNutritionLog.query.filter_by(
        user_id=current_user.id,
        date=selected_date
    ).all()

    # Calculate actual consumed totals
    day_totals = {
        'calories': sum(l.calories for l in daily_logs),
        'protein': sum(l.protein for l in daily_logs),
        'carbs': sum(l.carbs for l in daily_logs),
        'fat': sum(l.fat for l in daily_logs),
        'fiber': sum(l.fiber for l in daily_logs)
    }

    # Compare with active plan targets
    active_plan = MealPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    all_foods = FoodItem.query.order_by(FoodItem.name).all()

    return render_template(
        'nutrition/log.html',
        selected_date=selected_date.strftime('%Y-%m-%d'),
        daily_logs=daily_logs,
        day_totals=day_totals,
        active_plan=active_plan,
        all_foods=all_foods
    )


@nutrition_bp.route('/log/<int:log_id>/delete', methods=['POST'])
@login_required
def delete_log(log_id):
    entry = DailyNutritionLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    entry_date = entry.date.strftime('%Y-%m-%d')
    db.session.delete(entry)
    db.session.commit()
    flash(f'Removed {entry.food_name} from daily log.', 'info')
    return redirect(url_for('nutrition.log_food', date=entry_date))


@nutrition_bp.route('/foods')
def foods():
    category = request.args.get('category')
    diet = request.args.get('diet')
    query_str = request.args.get('q', '').strip()

    query = FoodItem.query
    if category:
        query = query.filter_by(category=category)
    if diet:
        query = query.filter_by(diet_type=diet)
    if query_str:
        query = query.filter(FoodItem.name.ilike(f'%{query_str}%'))

    items = query.order_by(FoodItem.name).all()
    categories = db.session.query(FoodItem.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('nutrition/foods.html', items=items, categories=categories, current_cat=category, current_diet=diet, search_q=query_str)
