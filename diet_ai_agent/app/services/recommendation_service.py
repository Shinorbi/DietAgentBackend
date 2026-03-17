from ..agent.diet_agent import diet_agent

def get_diet_recommendations(query):
    """
    Get diet recommendations using the AI agent
    """
    try:
        response = diet_agent.run(query)
        return {
            "success": True,
            "recommendation": response
        }
    except Exception as e:
        return {"error": f"Failed to get recommendations: {str(e)}"}

def analyze_meal_with_ai(meal_list):
    """
    Analyze a meal using the AI agent
    """
    try:
        meal_description = ", ".join([f"{item['qty']} {item['name']}" for item in meal_list])
        query = f"Analyze this meal: {meal_description}. Provide nutritional breakdown and suggestions for improvement."
        response = diet_agent.run(query)
        return {
            "success": True,
            "analysis": response
        }
    except Exception as e:
        return {"error": f"Failed to analyze meal: {str(e)}"}