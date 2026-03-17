from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from ..tools.calorie_tool import analyze_meal
from ..tools.diet_planner_tool import generate_diet_plan, generate_full_diet_plan
from ..tools.meal_analyzer_tool import analyze_meal_log, suggest_improvements
from ..tools.food_lookup_tool import lookup_food_knowledge, get_food_recommendations
from ..agent.prompts import SYSTEM_PROMPT
import json
import os
import re
from ..database.db import create_connection

# Load environment variables
load_dotenv()

# Initialize database connection
conn = create_connection()
if conn:
    print("Database connection established")
else:
    print("Database connection failed")

class DietAgent:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self._has_llm = bool(api_key)
        self.llm = None
        if self._has_llm:
            self.llm = ChatOpenAI(
                model="stepfun/step-3.5-flash:free",
                openai_api_base="https://openrouter.ai/api/v1",
                openai_api_key=api_key,
                temperature=0.7,
                max_tokens=8000,
                timeout=20,  # a bit more breathing room for OpenRouter
                model_kwargs={"response_format": {"type": "json_object"}},
            )

    def _parse_tools(self, query):
        """Parse the query to determine which tool to use"""
        if "analyze this meal" in query.lower():
            return "AnalyzeMeal"
        # Order matters: "diet plan" text often appears inside knowledge questions.
        elif "knowledge" in query.lower() or "information" in query.lower():
            return "LookupFoodKnowledge"
        elif "diet plan" in query.lower() or "meal plan" in query.lower() or "weekly plan" in query.lower() or "month" in query.lower():
            return "GenerateFullDietPlan"
        elif "calories" in query.lower():
            return "GenerateDietPlan"
        elif "recommend" in query.lower() or "suggest" in query.lower():
            return "GetFoodRecommendations"
        return None

    def _execute_tool(self, tool_name, input_data):
        """Execute the appropriate tool based on the tool name"""
        if tool_name == "AnalyzeMeal":
            return analyze_meal(input_data)
        elif tool_name == "GenerateDietPlan":
            return generate_diet_plan(**input_data)
        elif tool_name == "GenerateFullDietPlan":
            return generate_full_diet_plan(**input_data)
        elif tool_name == "GetFoodRecommendations":
            return get_food_recommendations(input_data["meal_type"], input_data.get("goal", "maintain_weight"))
        elif tool_name == "LookupFoodKnowledge":
            return lookup_food_knowledge(input_data)
        return None

    def run(self, query):
        """Run the agent with a user query"""
        try:
            # Simple tool parsing logic
            tool_name = self._parse_tools(query)
            if tool_name:
                # Extract input data from query
                if tool_name == "AnalyzeMeal":
                    # Extract foods from query
                    foods = self._extract_foods(query)
                    result = analyze_meal(foods)
                    return f"Analysis result: {result}"
                elif tool_name == "GenerateDietPlan":
                    # Extract user data from query
                    user_data = self._extract_user_data(query)
                    result = generate_diet_plan(**user_data)
                    return f"Diet plan: {result}"
                elif tool_name == "GenerateFullDietPlan":
                    user_data = self._extract_user_data(query, full=True)
                    result = generate_full_diet_plan(**user_data)
                    return json.dumps(result, ensure_ascii=False)
                elif tool_name == "GetFoodRecommendations":
                    # Extract meal type and goal
                    meal_type = self._extract_meal_type(query)
                    goal = self._extract_goal(query)
                    result = get_food_recommendations(meal_type, goal)
                    return f"Recommendations: {result}"
                elif tool_name == "LookupFoodKnowledge":
                    # Extract food query
                    food_query = self._extract_food_query(query)
                    result = lookup_food_knowledge(food_query)
                    return f"Knowledge: {result}"
            else:
                # If no tool detected, just use the LLM directly
                if not self._has_llm or self.llm is None:
                    return "LLM is not configured. Set OPENROUTER_API_KEY (preferred) or OPENAI_API_KEY to enable chat answers."
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ]
                response = self.llm.invoke(messages)
                return response.content
        except Exception as e:
            return f"Error processing your request: {str(e)}"

    def _extract_foods(self, query):
        """Extract foods from a meal analysis query"""
        # Simple extraction logic - in a real implementation this would be more sophisticated
        return [{"name": "egg", "qty": 2}, {"name": "toast", "qty": 1}]

    def _extract_user_data(self, query):
        """Extract user data from a diet plan query"""
        return self._extract_user_data(query, full=False)

    def _extract_user_data(self, query, full: bool = False):
        """
        Extract user data from free text.
        - If query contains a JSON object, parse it and use keys directly.
        - Otherwise, best-effort regex extraction with safe defaults.
        """
        q = query.strip()

        # 1) JSON override (lets the caller supply demographics/budget/preferences precisely)
        start = q.find("{")
        end = q.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(q[start : end + 1])
                if isinstance(data, dict):
                    # Normalize common fields
                    data.setdefault("goal", self._extract_goal(q))
                    data.setdefault("activity_level", "moderate")
                    if full and ("days" not in data):
                        data["days"] = 30 if "month" in q.lower() else 7
                    if full and ("meals_per_day" not in data):
                        data["meals_per_day"] = 3
                    return data
            except Exception:
                pass

        # 2) Regex extraction (fallback)
        def _num(pattern: str):
            m = re.search(pattern, q, flags=re.IGNORECASE)
            return float(m.group(1)) if m else None

        age = _num(r"(\d{2})\s*[- ]?year[- ]?old") or 25
        weight = _num(r"(\d+(?:\.\d+)?)\s*kg") or 70
        height = _num(r"(\d+(?:\.\d+)?)\s*cm") or 170

        gender = "male" if re.search(r"\bmale\b", q, flags=re.IGNORECASE) else "female" if re.search(r"\bfemale\b", q, flags=re.IGNORECASE) else "male"
        activity_level = "moderate"
        if re.search(r"\bsedentary\b", q, flags=re.IGNORECASE):
            activity_level = "sedentary"
        elif re.search(r"\blight\b", q, flags=re.IGNORECASE):
            activity_level = "light"
        elif re.search(r"\bvery active\b", q, flags=re.IGNORECASE):
            activity_level = "very_active"
        elif re.search(r"\bactive\b", q, flags=re.IGNORECASE):
            activity_level = "active"

        goal = self._extract_goal(q)

        base = {
            "weight": weight,
            "height": height,
            "age": int(age),
            "gender": gender,
            "activity_level": activity_level,
            "goal": goal,
        }

        if full:
            base["days"] = 30 if "month" in q.lower() else 7
            base["meals_per_day"] = 3
        return base

    def _extract_meal_type(self, query):
        """Extract meal type from a recommendation query"""
        if "breakfast" in query.lower():
            return "breakfast"
        elif "lunch" in query.lower():
            return "lunch"
        elif "dinner" in query.lower():
            return "dinner"
        return "breakfast"

    def _extract_goal(self, query):
        """Extract goal from a recommendation query"""
        if "lose weight" in query.lower():
            return "lose_weight"
        elif "gain weight" in query.lower():
            return "gain_weight"
        return "maintain_weight"

    def _extract_food_query(self, query):
        """Extract food query from a knowledge lookup query"""
        return query.replace("?", "").strip()

# Create a global agent instance
diet_agent = DietAgent()
