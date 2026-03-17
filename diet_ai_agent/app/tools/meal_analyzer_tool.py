from ..database.models import MealAnalysis
from ..tools.calorie_tool import analyze_meal

def analyze_meal_log(meal_list):
    """
    Analyze a meal log and provide detailed breakdown
    """
    analysis = analyze_meal(meal_list)

    # Create a summary message
    summary = f"""
    Meal Analysis Summary:
    -------------------------
    Total Calories: {analysis.total_calories:.1f}
    Protein: {analysis.total_protein:.1f}g
    Carbs: {analysis.total_carbs:.1f}g
    Fat: {analysis.total_fat:.1f}g

    Macronutrient Distribution:
    Protein: {analysis.total_protein * 4 / analysis.total_calories * 100:.1f}%
    Carbs: {analysis.total_carbs * 4 / analysis.total_calories * 100:.1f}%
    Fat: {analysis.total_fat * 9 / analysis.total_calories * 100:.1f}%
    """

    return {
        "analysis": analysis,
        "summary": summary.strip()
    }

def suggest_improvements(analysis, goal="maintain_weight"):
    """
    Suggest improvements based on meal analysis and user goal
    """
    suggestions = []

    # Check if meal is balanced
    protein_percentage = analysis.total_protein * 4 / analysis.total_calories * 100
    carbs_percentage = analysis.total_carbs * 4 / analysis.total_calories * 100
    fat_percentage = analysis.total_fat * 9 / analysis.total_calories * 100

    # Protein check
    if protein_percentage < 25:
        suggestions.append("Add more protein to your meal for better satiety and muscle maintenance.")
    elif protein_percentage > 35:
        suggestions.append("Your protein intake is high. Consider balancing with more carbs or fats.")

    # Carb check
    if carbs_percentage < 20:
        suggestions.append("Add complex carbohydrates for sustained energy.")
    elif carbs_percentage > 50:
        suggestions.append("Reduce refined carbs and add more protein or healthy fats.")

    # Fat check
    if fat_percentage < 20:
        suggestions.append("Include healthy fats like avocado, nuts, or olive oil.")
    elif fat_percentage > 40:
        suggestions.append("Reduce fat intake and add more protein or complex carbs.")

    # Calorie check based on goal
    if goal == "lose_weight" and analysis.total_calories > 600:
        suggestions.append("For weight loss, consider reducing portion sizes or choosing lower-calorie options.")
    elif goal == "gain_weight" and analysis.total_calories < 800:
        suggestions.append("For weight gain, add calorie-dense foods like nuts, seeds, or healthy oils.")

    return suggestions