from ..vectorstore.chroma_store import lookup_food_knowledge

def get_food_recommendations(meal_type, goal="maintain_weight"):
    """
    Get food recommendations based on meal type and goal
    """
    recommendations = {
        "breakfast": {
            "maintain_weight": [
                "Eggs with whole grain toast and avocado",
                "Greek yogurt with berries and nuts",
                "Oatmeal with protein powder and banana"
            ],
            "lose_weight": [
                "Egg white omelet with vegetables",
                "Protein smoothie with spinach and berries",
                "Cottage cheese with cucumber and tomatoes"
            ],
            "gain_weight": [
                "Peanut butter banana smoothie",
                "Avocado toast with eggs",
                "Greek yogurt parfait with granola"
            ]
        },
        "lunch": {
            "maintain_weight": [
                "Grilled chicken salad with quinoa",
                "Turkey wrap with vegetables",
                "Salmon with sweet potato and broccoli"
            ],
            "lose_weight": [
                "Grilled chicken with mixed greens",
                "Tuna salad with light dressing",
                "Vegetable soup with lean protein"
            ],
            "gain_weight": [
                "Beef stir-fry with rice",
                "Chicken avocado sandwich",
                "Pasta with meat sauce and vegetables"
            ]
        },
        "dinner": {
            "maintain_weight": [
                "Baked fish with roasted vegetables",
                "Lean steak with sweet potato",
                "Tofu stir-fry with brown rice"
            ],
            "lose_weight": [
                "Grilled chicken with steamed vegetables",
                "Shrimp salad with light dressing",
                "Vegetable curry with cauliflower rice"
            ],
            "gain_weight": [
                "Pork chops with mashed potatoes",
                "Salmon with quinoa and asparagus",
                "Lamb with roasted vegetables"
            ]
        }
    }

    if meal_type in recommendations:
        return recommendations[meal_type].get(goal, recommendations[meal_type]["maintain_weight"])
    return ["I couldn't find recommendations for that meal type. Please try breakfast, lunch, or dinner."]
