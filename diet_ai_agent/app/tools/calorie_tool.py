from ..database.models import FoodItem, MealAnalysis

# Food calorie database
FOOD_DATABASE = {
    "egg": FoodItem(name="egg", calories=78, protein=6.3, carbs=0.6, fat=5.0),
    "rice": FoodItem(name="rice", calories=200, protein=4.3, carbs=44.5, fat=0.3),
    "chicken": FoodItem(name="chicken", calories=165, protein=31.0, carbs=0.0, fat=3.6),
    "dal": FoodItem(name="dal", calories=180, protein=8.0, carbs=30.0, fat=2.0),
    "toast": FoodItem(name="toast", calories=80, protein=2.0, carbs=15.0, fat=1.0),
    "oats": FoodItem(name="oats", calories=150, protein=5.0, carbs=27.0, fat=2.5),
    "almonds": FoodItem(name="almonds", calories=164, protein=6.0, carbs=6.0, fat=14.0),
    "yogurt": FoodItem(name="yogurt", calories=100, protein=10.0, carbs=12.0, fat=2.0),
    "salmon": FoodItem(name="salmon", calories=208, protein=20.0, carbs=0.0, fat=13.0),
    "quinoa": FoodItem(name="quinoa", calories=120, protein=4.0, carbs=21.0, fat=1.9),
    "sweet_potato": FoodItem(name="sweet_potato", calories=103, protein=2.3, carbs=24.0, fat=0.1),
    "broccoli": FoodItem(name="broccoli", calories=34, protein=2.8, carbs=7.0, fat=0.4),
    "avocado": FoodItem(name="avocado", calories=160, protein=2.0, carbs=9.0, fat=15.0),
    "lentils": FoodItem(name="lentils", calories=116, protein=9.0, carbs=20.0, fat=0.4),
    "chia_seeds": FoodItem(name="chia_seeds", calories=138, protein=4.7, carbs=12.3, fat=8.7),
    "tofu": FoodItem(name="tofu", calories=76, protein=8.0, carbs=2.0, fat=4.8),
    "berries": FoodItem(name="berries", calories=50, protein=1.0, carbs=12.0, fat=0.5),
    "spinach": FoodItem(name="spinach", calories=7, protein=0.9, carbs=1.1, fat=0.1),
    "brown_rice": FoodItem(name="brown_rice", calories=111, protein=2.6, carbs=23.0, fat=0.9)
}

def calculate_calories(food_name, quantity):
    """
    Calculate calories for a specific food item
    """
    food_name = food_name.lower().replace(" ", "_")
    if food_name in FOOD_DATABASE:
        food = FOOD_DATABASE[food_name]
        return {
            "name": food.name,
            "calories": food.calories * quantity,
            "protein": food.protein * quantity,
            "carbs": food.carbs * quantity,
            "fat": food.fat * quantity
        }
    return None

def analyze_meal(meal_list):
    """
    Analyze a list of foods with quantities
    """
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    analyzed_foods = []

    for item in meal_list:
        result = calculate_calories(item["name"], item["qty"])
        if result:
            total_calories += result["calories"]
            total_protein += result["protein"]
            total_carbs += result["carbs"]
            total_fat += result["fat"]
            analyzed_foods.append(result)

    return MealAnalysis(
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        foods=analyzed_foods
    )