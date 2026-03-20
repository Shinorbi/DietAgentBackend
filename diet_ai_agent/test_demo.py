from app.agent.diet_agent import diet_agent
import json
import os

def _print_section(title: str):
    print(title)
    print("-" * len(title))

def _pretty_print_result(result):
    # Agent may return a string, or JSON string for full plans.
    if isinstance(result, str):
        s = result.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                obj = json.loads(s)
                print(json.dumps(obj, indent=2, ensure_ascii=False)[:12000])
                return
            except Exception:
                pass
        print(result)
        return
    print(result)

def test_agent():
    print("Testing Diet Agent...\n")
    print("Env check:")
    print(f"- OPENROUTER_API_KEY set: {bool(os.getenv('OPENROUTER_API_KEY'))}")
    print(f"- OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")
    print("\n" + "="*50 + "\n")

    # Test 1: General query
    _print_section("1) General Query (LLM chat)")
    _pretty_print_result(diet_agent.run("What are the benefits of eating napoles styple pizza?"))
    print("\n" + "="*50 + "\n")

    # Test 2: Meal analysis
    _print_section("2) Meal Analysis (local calorie tool)")
    _pretty_print_result(diet_agent.run("Analyze this meal: 2 eggs, 1 toast"))
    print("\n" + "="*50 + "\n")

    # Test 3: Diet plan
    _print_section("3) Calories + Macros Targets (non-LLM)")
    _pretty_print_result(
        diet_agent.run(
            "Create calories and macros for a 25-year-old male, 70kg, 170cm, moderate activity, wanting to maintain weight"
        )
    )
    print("\n" + "="*50 + "\n")

    # Test 4: Food knowledge
    _print_section("4) Food Knowledge (local store)")
    _pretty_print_result(diet_agent.run("Give me knowledge about rice vs brown rice for weight loss."))
    print("\n" + "="*50 + "\n")

    # Test 5+: Full meal plan across multiple demographics/goals (LLM)
    scenarios = [
        # {
        #     "label": "5A) Bangladesh / Bengali / male / 25 / weight loss",
        #     "payload": {
        #         "weight": 70,
        #         "height": 170,
        #         "age": 25,
        #         "gender": "male",
        #         "activity_level": "moderate",
        #         "goal": "lose_weight",
        #         "days": 7,
        #         "meals_per_day": 3,
        #         "country": "Bangladesh",
        #         "currency": "BDT",
        #         "budget_per_day": 350,
        #         "cuisine_preferences": ["bengali"],
        #         "dietary_restrictions": ["halal"],
        #         "allergies": [],
        #         "cooking_time_per_day_minutes": 30,
        #         "cooking_level": "beginner",
        #         "equipment": ["stove", "rice cooker"],
        #     },
        # },
        # {
        #     "label": "5B) Bangladesh / Bengali / female / 35 / weight loss",
        #     "payload": {
        #         "weight": 68,
        #         "height": 160,
        #         "age": 35,
        #         "gender": "female",
        #         "activity_level": "light",
        #         "goal": "lose_weight",
        #         "days": 7,
        #         "meals_per_day": 3,
        #         "country": "Bangladesh",
        #         "currency": "BDT",
        #         "budget_per_day": 300,
        #         "cuisine_preferences": ["bengali"],
        #         "dietary_restrictions": ["halal"],
        #         "allergies": [],
        #         "cooking_time_per_day_minutes": 30,
        #         "cooking_level": "beginner",
        #         "equipment": ["stove"],
        #     },
        # },
        # {
        #     "label": "5C) Bangladesh / Bengali / male / 22 / weight gain",
        #     "payload": {
        #         "weight": 60,
        #         "height": 170,
        #         "age": 22,
        #         "gender": "male",
        #         "activity_level": "active",
        #         "goal": "gain_weight",
        #         "days": 7,
        #         "meals_per_day": 4,
        #         "country": "Bangladesh",
        #         "currency": "BDT",
        #         "budget_per_day": 450,
        #         "cuisine_preferences": ["bengali"],
        #         "dietary_restrictions": ["halal"],
        #         "allergies": [],
        #         "cooking_time_per_day_minutes": 45,
        #         "cooking_level": "beginner",
        #         "equipment": ["stove", "rice cooker"],
        #     },
        # },
        {
            "label": "5D) USA / vegetarian / female / 29 / maintenance",
            "payload": {
                "weight": 63,
                "height": 165,
                "age": 29,
                "gender": "female",
                "activity_level": "moderate",
                "goal": "maintain_weight",
                "days": 7,
                "meals_per_day": 3,
                "country": "ITALY",
                "currency": "EUR",
                "budget_per_day": 20,
                "cuisine_preferences": ["ITALIAN"],
                "dietary_restrictions": ["non-vegetarian"],
                "allergies": ["peanut"],
                "cooking_time_per_day_minutes": 25,
                "cooking_level": "beginner",
                "equipment": ["stove", "microwave"],
            },
        },
    ]

    for sc in scenarios:
        _print_section(sc["label"])
        result = diet_agent.run("Generate a full diet plan " + json.dumps(sc["payload"]))
        _pretty_print_result(result)
        print("\n" + "="*50 + "\n")

    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_agent()