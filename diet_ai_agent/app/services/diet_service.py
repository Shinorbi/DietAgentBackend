from ..tools.diet_planner_tool import generate_diet_plan, generate_full_diet_plan
from ..database.models import DietPlan

def create_diet_plan(user_data):
    """
    Create a diet plan for a user
    """
    try:
        weight = float(user_data.get("weight", 70))
        height = float(user_data.get("height", 170))
        age = int(user_data.get("age", 25))
        gender = user_data.get("gender", "male")
        activity_level = user_data.get("activity_level", "moderate")
        goal = user_data.get("goal", "maintain_weight")

        # Optional "MyFitnessPal-style" fields
        days = int(user_data.get("days", 7) or 7)
        meals_per_day = int(user_data.get("meals_per_day", 3) or 3)
        country = user_data.get("country")
        currency = user_data.get("currency", "USD")
        budget_per_day = user_data.get("budget_per_day")
        budget_per_week = user_data.get("budget_per_week")
        cooking_time_per_day_minutes = user_data.get("cooking_time_per_day_minutes")
        cooking_level = user_data.get("cooking_level")
        cuisine_preferences = user_data.get("cuisine_preferences") or []
        dietary_restrictions = user_data.get("dietary_restrictions") or []
        allergies = user_data.get("allergies") or []
        equipment = user_data.get("equipment") or []

        # Always compute targets; then generate full plan via LLM.
        targets = generate_diet_plan(weight, height, age, gender, activity_level, goal)
        full_plan = generate_full_diet_plan(
            weight=weight,
            height=height,
            age=age,
            gender=gender,
            activity_level=activity_level,
            goal=goal,
            days=days,
            meals_per_day=meals_per_day,
            country=country,
            cuisine_preferences=cuisine_preferences,
            dietary_restrictions=dietary_restrictions,
            allergies=allergies,
            budget_per_day=float(budget_per_day) if budget_per_day is not None else None,
            budget_per_week=float(budget_per_week) if budget_per_week is not None else None,
            currency=currency,
            cooking_time_per_day_minutes=int(cooking_time_per_day_minutes) if cooking_time_per_day_minutes is not None else None,
            cooking_level=cooking_level,
            equipment=equipment,
        )

        return {
            "targets": targets,
            "full_plan": full_plan,
        }
    except Exception as e:
        return {"error": f"Failed to create diet plan: {str(e)}"}

def get_macros_breakdown(diet_plan):
    """
    Get a formatted macros breakdown
    """
    if isinstance(diet_plan, dict) and "error" in diet_plan:
        return diet_plan

    # If the service returns a wrapped dict, normalize.
    if isinstance(diet_plan, dict) and "targets" in diet_plan:
        diet_plan = diet_plan["targets"]

    if isinstance(diet_plan, dict):
        daily_calories = float(diet_plan.get("daily_calories", 0) or 0)
        protein_grams = float(diet_plan.get("protein_grams", 0) or 0)
        carbs_grams = float(diet_plan.get("carbs_grams", 0) or 0)
        fat_grams = float(diet_plan.get("fat_grams", 0) or 0)
        if daily_calories <= 0:
            return {"error": "Invalid diet plan targets (daily_calories missing)."}
        return {
            "daily_calories": int(daily_calories),
            "protein": f"{protein_grams}g",
            "carbs": f"{carbs_grams}g",
            "fat": f"{fat_grams}g",
            "protein_percentage": f"{(protein_grams * 4 / daily_calories * 100):.1f}%",
            "carbs_percentage": f"{(carbs_grams * 4 / daily_calories * 100):.1f}%",
            "fat_percentage": f"{(fat_grams * 9 / daily_calories * 100):.1f}%"
        }

    return {
        "daily_calories": diet_plan.daily_calories,
        "protein": f"{diet_plan.protein_grams}g",
        "carbs": f"{diet_plan.carbs_grams}g",
        "fat": f"{diet_plan.fat_grams}g",
        "protein_percentage": f"{(diet_plan.protein_grams * 4 / diet_plan.daily_calories * 100):.1f}%",
        "carbs_percentage": f"{(diet_plan.carbs_grams * 4 / diet_plan.daily_calories * 100):.1f}%",
        "fat_percentage": f"{(diet_plan.fat_grams * 9 / diet_plan.daily_calories * 100):.1f}%"
    }