def _estimate_daily_calories(weight_kg: float, activity_level: str, goal: str):
    baseline = max(1200, weight_kg * 30)
    activity_multiplier = {"low": 1.0, "medium": 1.1, "high": 1.2}.get(activity_level, 1.0)
    calories = baseline * activity_multiplier

    if goal == "weight_loss":
        calories -= 300
    elif goal == "weight_gain":
        calories += 300

    return int(max(1200, calories))


def generate_fitness_diet_plan(form_data: dict):
    """Generate a supportive nutrition and movement plan from user profile."""
    errors = []

    try:
        age = int(form_data.get("age", "0"))
        height_cm = float(form_data.get("height_cm", "0"))
        weight_kg = float(form_data.get("weight_kg", "0"))
    except ValueError:
        return None, ["Age, height, and weight must be valid numbers."]

    if age < 13 or age > 60:
        errors.append("Please enter an age between 13 and 60 for this educational planner.")
    if height_cm < 120 or height_cm > 210:
        errors.append("Height should be between 120 cm and 210 cm.")
    if weight_kg < 30 or weight_kg > 180:
        errors.append("Weight should be between 30 kg and 180 kg.")

    goal = form_data.get("goal", "maintenance")
    activity_level = form_data.get("activity_level", "low")
    thyroid = form_data.get("thyroid", "no")
    pcos = form_data.get("pcos", "no")
    pregnancy = form_data.get("pregnancy", "no")

    if errors:
        return None, errors

    calories = _estimate_daily_calories(weight_kg, activity_level, goal)

    base_plan = {
        "breakfast": "Oats or poha with nuts and fruit",
        "lunch": "Whole grains, dal/lean protein, cooked vegetables, salad",
        "dinner": "Light protein-rich meal with vegetables and soup",
        "snacks": "Fruit, roasted chana, yogurt, or handful of seeds",
        "water": "2.5 to 3 liters daily",
    }

    notes = []
    fitness_tips = [
        "30-minute brisk walking most days",
        "15-minute light strength or mobility routine",
        "Gentle yoga and stretching for stress relief",
    ]

    if goal == "weight_loss":
        notes.append("Focus on portion control and low-calorie dense foods.")
        base_plan["dinner"] = "Vegetable-rich, high-fiber light dinner with lean protein"
    elif goal == "weight_gain":
        notes.append("Add healthy calorie surplus with proteins and good fats.")
        base_plan["snacks"] = "Peanut butter toast, banana shake, mixed nuts, yogurt"

    if thyroid == "yes":
        notes.append("Include iodine-balanced foods and selenium sources (as advised medically).")

    if pcos == "yes":
        notes.append("Prefer low-sugar, high-fiber meals and reduce ultra-processed foods.")

    if pregnancy == "yes":
        notes.append("Prioritize safe prenatal nutrition and avoid unsafe food items.")
        fitness_tips = [
            "Daily gentle walk as advised by your doctor",
            "Prenatal yoga or breathing practice if medically cleared",
            "Avoid high-impact workouts without medical guidance",
        ]

    progress_steps = [
        {"title": "Profile Added", "done": True},
        {"title": "Goal Selected", "done": True},
        {"title": "Condition Aware Plan", "done": True},
        {"title": "Daily Routine Ready", "done": True},
    ]

    return {
        "calories": calories,
        "plan": base_plan,
        "notes": notes,
        "fitness_tips": fitness_tips,
        "progress_steps": progress_steps,
    }, []
