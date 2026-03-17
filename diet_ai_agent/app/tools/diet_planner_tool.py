from ..database.models import DietPlan
from typing import Any, Dict, List, Optional, Tuple
import json

from ..llm.openrouter_llm import get_llm

def calculate_daily_calories(weight, height, age, gender, activity_level, goal):
    """
    Calculate daily calorie needs using Mifflin-St Jeor Equation
    """
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity level multipliers
    activity_multipliers = {
        "sedentary": 1.2,      # Little or no exercise
        "light": 1.375,        # Light exercise 1-3 days/week
        "moderate": 1.55,      # Moderate exercise 3-5 days/week
        "active": 1.725,       # Hard exercise 6-7 days a week
        "very_active": 1.9     # Very hard exercise & physical job
    }

    maintenance_calories = bmr * activity_multipliers.get(activity_level, 1.2)

    # Adjust for goal
    if goal == "lose_weight":
        daily_calories = maintenance_calories - 500
    elif goal == "gain_weight":
        daily_calories = maintenance_calories + 500
    else:  # maintain_weight
        daily_calories = maintenance_calories

    return max(1200, int(daily_calories))  # Minimum 1200 calories

def calculate_macros(daily_calories):
    """
    Calculate macro distribution (40% protein, 30% carbs, 30% fat)
    """
    protein_calories = daily_calories * 0.4
    carbs_calories = daily_calories * 0.3
    fat_calories = daily_calories * 0.3

    protein_grams = protein_calories / 4
    carbs_grams = carbs_calories / 4
    fat_grams = fat_calories / 9

    return {
        "daily_calories": daily_calories,
        "protein_grams": round(protein_grams, 1),
        "carbs_grams": round(carbs_grams, 1),
        "fat_grams": round(fat_grams, 1)
    }

def _safe_json_loads(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except Exception:
        return None

def _extract_json_object(text: str) -> Optional[dict]:
    """
    Best-effort extraction if model wraps JSON in markdown fences or extra text.
    """
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return _safe_json_loads(text[start : end + 1])

def _macro_targets_from_calories(daily_calories: int, split: Tuple[float, float, float]) -> Dict[str, float]:
    """
    Returns grams for protein/carbs/fat based on calorie split.
    split = (protein_pct, carbs_pct, fat_pct) that should sum to 1.
    """
    p_pct, c_pct, f_pct = split
    protein_g = (daily_calories * p_pct) / 4
    carbs_g = (daily_calories * c_pct) / 4
    fat_g = (daily_calories * f_pct) / 9
    return {
        "daily_calories": int(daily_calories),
        "protein_grams": round(protein_g, 1),
        "carbs_grams": round(carbs_g, 1),
        "fat_grams": round(fat_g, 1),
        "macro_split": {"protein": p_pct, "carbs": c_pct, "fat": f_pct},
    }

def _build_portion_guidelines(
    *,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    meals_per_day: int,
    country: Optional[str] = None,
    cuisine_preferences: Optional[List[str]] = None,
    dietary_restrictions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    # Rough per-meal targets (useful for portioning regular meals)
    meals = max(2, int(meals_per_day or 3))
    per_meal_protein = round(protein_g / meals, 1)
    per_meal_carbs = round(carbs_g / meals, 1)
    per_meal_fat = round(fat_g / meals, 1)

    cuisine = [c.lower() for c in (cuisine_preferences or [])]
    restrictions = [r.lower() for r in (dietary_restrictions or [])]
    country_l = (country or "").lower()

    is_bengali = ("bengali" in cuisine) or ("bangladesh" in country_l) or ("kolkata" in country_l)
    is_vegetarian = any(r in restrictions for r in ["vegetarian", "vegan"])

    protein_examples = (
        "egg/Greek yogurt/tofu/tempeh/dal"
        if is_vegetarian
        else "fish/chicken/eggs/dal"
    )

    guidelines: Dict[str, Any] = {
        "plate_method": [
            "At main meals: 1/2 plate non-starchy vegetables, 1/4 plate protein, 1/4 plate carbs (rice/roti).",
            f"Aim per meal around ~{per_meal_protein}g protein, ~{per_meal_carbs}g carbs, ~{per_meal_fat}g fat (flexible).",
        ],
        "hand_portion_method": [
            f"Protein: 1 palm-equivalent per meal (examples: {protein_examples}). If using meat/fish, ~90–120g cooked is a good start.",
            "Carbs: 1 cupped-hand cooked starch (~1/2 cup cooked rice/pasta) OR 1 slice bread/1 medium roti; adjust up/down based on hunger/training.",
            "Fats: 1 thumb oil/ghee (~1 tsp) per meal; keep frying oil minimal.",
            "Vegetables: 2 fists of vegetables per main meal (more is fine).",
        ],
        "how_to_handle_regular_meal": [
            "Start by fixing portions (protein + veg first). Keep cooking oil low, and measure starch (rice/roti/bread/pasta) instead of guessing.",
            "If you must eat a heavier/oilier meal: reduce starch by ~50% and skip sweets/sugary drinks that day.",
            "If you’re still hungry: add more vegetables/salad first, then add lean protein; only then add extra rice.",
        ],
    }

    if is_bengali:
        guidelines["regional_staples_portions"] = {
            "region": "bengali",
            "cooked_rice_cups": {
                "light_day": 1.0,
                "training_day": 1.5,
                "notes": "Spread across lunch+dinner. Example: 1/2 cup at lunch + 1/2 cup at dinner (light day).",
            },
            "roti_pieces": {"range": "1–3/day", "notes": "If using roti instead of rice, keep to 1 roti per meal to start."},
            "dal_cups": {"range": "1–2 cups/day", "notes": "Prefer thicker dal (less oil). Dal counts as both protein+carbs."},
            "protein_curry_cooked_g": {
                "range": "180–300g/day",
                "notes": "Fish/chicken/egg curry: prioritize the protein portion; keep gravy oil low.",
            },
            "vegetables_cups": {"minimum": 4, "notes": "Aim at least 2 cups lunch + 2 cups dinner (shobji/bhaji/salad)."},
            "oil_teaspoons_per_meal": {"range": "1–2 tsp", "notes": "Includes cooking oil + added oil. Avoid deep-fry most days."},
        }
        guidelines["how_to_handle_regular_meal"] = [
            "If you eat a Bengali plate (bhaat + dal + machh/murgi + shobji): keep rice to ~1/2 cup cooked per meal, keep protein to 1–1.5 palms cooked, add plenty of vegetables, and limit oil to 1–2 tsp total.",
            "If you must eat biriyani/tehari/fried snacks: halve rice, add extra salad/veg, and make the next meal protein+veg focused.",
            "If you’re still hungry: add more vegetables/salad first, then add lean protein; only then add extra rice.",
        ]
    else:
        guidelines["regional_staples_portions"] = {
            "region": "general",
            "starches": {
                "per_meal_examples": [
                    "1/2 cup cooked rice/pasta",
                    "1 medium potato",
                    "1 slice bread",
                    "1 small tortilla",
                ],
                "notes": "Pick ONE starch per meal; if you snack on carbs, reduce the meal starch a bit.",
            },
            "proteins": {
                "per_meal_examples": [
                    "90–150g cooked chicken/fish",
                    "2–3 eggs",
                    "1 cup Greek yogurt/cottage cheese",
                    "1–1.5 cups beans/lentils/tofu (vegetarian)",
                ],
                "notes": "If vegetarian, use tofu/beans/lentils + dairy/eggs (if allowed) to hit protein.",
            },
            "fats": {"per_meal": "1–2 tsp oil OR a small handful of nuts", "notes": "Fats add up fast—measure oils."},
        }

    return guidelines

def generate_diet_plan(weight, height, age, gender, activity_level, goal):
    """
    Generate calorie + macro targets (legacy/basic plan).
    """
    daily_calories = calculate_daily_calories(weight, height, age, gender, activity_level, goal)
    macros = calculate_macros(daily_calories)

    return {
        "daily_calories": macros["daily_calories"],
        "protein_grams": macros["protein_grams"],
        "carbs_grams": macros["carbs_grams"],
        "fat_grams": macros["fat_grams"]
    }

def generate_full_diet_plan(
    *,
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str,
    days: int = 7,
    meals_per_day: int = 3,
    country: Optional[str] = None,
    cuisine_preferences: Optional[List[str]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
    budget_per_day: Optional[float] = None,
    budget_per_week: Optional[float] = None,
    currency: str = "USD",
    cooking_time_per_day_minutes: Optional[int] = None,
    cooking_level: Optional[str] = None,
    equipment: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    MyFitnessPal-style output:
    - demographics-aware assumptions
    - calorie + macro targets
    - multi-day meal plan with foods + portions + estimated macros
    - budgeted shopping list and substitutions
    """
    # Keep LLM output compact to avoid OpenRouter length limits.
    # We generate a small "rotation" plan and include instructions to repeat/scale it.
    requested_days = max(1, int(days or 7))
    days = max(1, min(requested_days, 3))
    meals_per_day = max(2, min(int(meals_per_day or 3), 6))

    calorie_targets = generate_diet_plan(weight, height, age, gender, activity_level, goal)
    # Slightly more balanced default split than the legacy 40/30/30:
    targets = _macro_targets_from_calories(int(calorie_targets["daily_calories"]), (0.30, 0.40, 0.30))
    portion_guidelines = _build_portion_guidelines(
        protein_g=float(targets["protein_grams"]),
        carbs_g=float(targets["carbs_grams"]),
        fat_g=float(targets["fat_grams"]),
        meals_per_day=meals_per_day,
        country=country,
        cuisine_preferences=cuisine_preferences,
        dietary_restrictions=dietary_restrictions,
    )

    try:
        llm = get_llm()
    except Exception as e:
        return {
            "profile_summary": {
                "demographics": {
                    "age": age,
                    "gender": gender,
                    "weight_kg": weight,
                    "height_cm": height,
                    "activity_level": activity_level,
                    "goal": goal,
                    "country": country,
                },
                "assumptions": [f"LLM not available: {str(e)}"],
                "constraints": {
                    "dietary_restrictions": dietary_restrictions or [],
                    "allergies": allergies or [],
                    "cuisine_preferences": cuisine_preferences or [],
                    "cooking_time_per_day_minutes": cooking_time_per_day_minutes,
                    "cooking_level": cooking_level,
                    "equipment": equipment or [],
                },
                "budget": {
                    "currency": currency,
                    "budget_per_day": budget_per_day,
                    "budget_per_week": budget_per_week,
                    "estimated_cost_per_day": 0,
                    "estimated_cost_per_week": 0,
                },
            },
            "targets": targets,
            "portion_guidelines": portion_guidelines,
            "meal_plan": {"days": []},
            "grocery_list": {"items": [], "estimated_total_cost": 0},
            "prep_plan": {"batch_cook_suggestions": [], "storage_notes": [], "swap_options": []},
            "tracking_tips": [],
        }

    prompt = f"""
You are a diet planning assistant. Create a realistic, budget-aware, demographic-aware meal plan.

User demographics & constraints:
- Age: {age}
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Activity level: {activity_level}
- Goal: {goal}
- Country/region: {country or "unknown"}
- Cuisine preferences: {", ".join(cuisine_preferences or []) or "none specified"}
- Dietary restrictions: {", ".join(dietary_restrictions or []) or "none"}
- Allergies: {", ".join(allergies or []) or "none"}
- Cooking time/day (minutes): {cooking_time_per_day_minutes or "unknown"}
- Cooking level: {cooking_level or "unknown"}
- Equipment: {", ".join(equipment or []) or "unknown"}
- Budget/day: {budget_per_day if budget_per_day is not None else "unknown"} {currency}
- Budget/week: {budget_per_week if budget_per_week is not None else "unknown"} {currency}

Nutrition targets (must follow closely):
- Daily calories: {targets["daily_calories"]}
- Protein grams: {targets["protein_grams"]}
- Carbs grams: {targets["carbs_grams"]}
- Fat grams: {targets["fat_grams"]}
- Meals per day: {meals_per_day}
- Days requested: {requested_days}
- Days to generate explicitly: {days} (rotation plan)

Output STRICT JSON only (no markdown, no extra text).
Keep the JSON concise (aim for under ~2500 tokens). Prefer repeating meals via a "rotation" rather than listing many unique recipes.

Use this schema:
{{
  "profile_summary": {{
    "demographics": {{
      "age": <int>, "gender": <str>, "weight_kg": <number>, "height_cm": <number>,
      "activity_level": <str>, "goal": <str>, "country": <str|null>
    }},
    "assumptions": [<str>, ...],
    "constraints": {{
      "dietary_restrictions": [<str>, ...],
      "allergies": [<str>, ...],
      "cuisine_preferences": [<str>, ...],
      "cooking_time_per_day_minutes": <int|null>,
      "cooking_level": <str|null>,
      "equipment": [<str>, ...]
    }},
    "budget": {{
      "currency": <str>,
      "budget_per_day": <number|null>,
      "budget_per_week": <number|null>,
      "estimated_cost_per_day": <number>,
      "estimated_cost_per_week": <number>
    }}
  }},
  "targets": {{
    "daily_calories": <int>,
    "protein_grams": <number>,
    "carbs_grams": <number>,
    "fat_grams": <number>,
    "macro_split": {{"protein": <number>, "carbs": <number>, "fat": <number>}}
  }},
  "portion_guidelines": {{
    "plate_method": [<str>, ...],
    "hand_portion_method": [<str>, ...],
    "bengali_staples_portions": {{
      "cooked_rice_cups": {{"light_day": <number>, "training_day": <number>, "notes": <str>}},
      "roti_pieces": {{"range": <str>, "notes": <str>}},
      "dal_cups": {{"range": <str>, "notes": <str>}},
      "chicken_or_fish_cooked_g": {{"range": <str>, "notes": <str>}},
      "vegetables_cups": {{"minimum": <number>, "notes": <str>}},
      "oil_teaspoons_per_meal": {{"range": <str>, "notes": <str>}}
    }},
    "how_to_handle_regular_meal": [
      <str>
    ]
  }},
  "meal_plan": {{
    "rotation_instructions": [<str>, ...],
    "days": [
      {{
        "day": <int>,
        "meals": [
          {{
            "name": <str>,  // e.g., "Breakfast"
            "items": [
              {{
                "food": <str>,
                "portion": <str>,          // e.g., "2 eggs", "1 cup cooked rice"
                "estimated_calories": <number>,
                "estimated_protein_g": <number>,
                "estimated_carbs_g": <number>,
                "estimated_fat_g": <number>,
                "notes": <str|null>
              }}
            ],
            "meal_totals": {{
              "calories": <number>, "protein_g": <number>, "carbs_g": <number>, "fat_g": <number>
            }}
          }}
        ],
        "day_totals": {{
          "calories": <number>, "protein_g": <number>, "carbs_g": <number>, "fat_g": <number>
        }}
      }}
    ]
  }},
  "grocery_list": {{
    "items": [
      {{
        "ingredient": <str>,
        "quantity": <str>,
        "category": <str>,              // produce/protein/grains/dairy/etc
        "estimated_cost": <number|null>
      }}
    ],
    "estimated_total_cost": <number>
  }},
  "prep_plan": {{
    "batch_cook_suggestions": [<str>, ...],
    "storage_notes": [<str>, ...],
    "swap_options": [{{"if_unavailable": <str>, "swap_with": <str>}}, ...]
  }},
  "tracking_tips": [<str>, ...]
}}

Rules:
- Keep foods common and purchasable in the user's region when country is provided.
- Keep the plan within budget if budget is provided; otherwise keep it low-to-moderate cost.
- Avoid allergens and respect restrictions.
- Ensure each day roughly hits the targets; small deviations are okay (±10% calories).
- IMPORTANT: Because Days requested may be > Days generated, include clear "rotation_instructions" to repeat the 3-day plan across {requested_days} days.
- Include portion guidance for Bengali regular meals (bhaat/dal/machh/chicken/vegetable bhaji) so the user can eat their normal food while staying on plan.
"""

    try:
        response = llm.invoke([{"role": "user", "content": prompt}])
        raw = getattr(response, "content", "") or ""
    except Exception as e:
        return {
            "profile_summary": {
                "demographics": {
                    "age": age,
                    "gender": gender,
                    "weight_kg": weight,
                    "height_cm": height,
                    "activity_level": activity_level,
                    "goal": goal,
                    "country": country,
                },
                "assumptions": [f"LLM call failed: {str(e)}"],
                "constraints": {
                    "dietary_restrictions": dietary_restrictions or [],
                    "allergies": allergies or [],
                    "cuisine_preferences": cuisine_preferences or [],
                    "cooking_time_per_day_minutes": cooking_time_per_day_minutes,
                    "cooking_level": cooking_level,
                    "equipment": equipment or [],
                },
                "budget": {
                    "currency": currency,
                    "budget_per_day": budget_per_day,
                    "budget_per_week": budget_per_week,
                    "estimated_cost_per_day": 0,
                    "estimated_cost_per_week": 0,
                },
            },
            "targets": targets,
            "portion_guidelines": portion_guidelines,
            "meal_plan": {"days": []},
            "grocery_list": {"items": [], "estimated_total_cost": 0},
            "prep_plan": {"batch_cook_suggestions": [], "storage_notes": [], "swap_options": []},
            "tracking_tips": [],
        }

    if not raw.strip():
        return {
            "profile_summary": {
                "demographics": {
                    "age": age,
                    "gender": gender,
                    "weight_kg": weight,
                    "height_cm": height,
                    "activity_level": activity_level,
                    "goal": goal,
                    "country": country,
                },
                "assumptions": ["LLM returned an empty response; returning targets only."],
                "constraints": {
                    "dietary_restrictions": dietary_restrictions or [],
                    "allergies": allergies or [],
                    "cuisine_preferences": cuisine_preferences or [],
                    "cooking_time_per_day_minutes": cooking_time_per_day_minutes,
                    "cooking_level": cooking_level,
                    "equipment": equipment or [],
                },
                "budget": {
                    "currency": currency,
                    "budget_per_day": budget_per_day,
                    "budget_per_week": budget_per_week,
                    "estimated_cost_per_day": 0,
                    "estimated_cost_per_week": 0,
                },
            },
            "targets": targets,
            "portion_guidelines": portion_guidelines,
            "meal_plan": {"days": []},
            "grocery_list": {"items": [], "estimated_total_cost": 0},
            "prep_plan": {"batch_cook_suggestions": [], "storage_notes": [], "swap_options": []},
            "tracking_tips": [],
        }
    parsed = _safe_json_loads(raw) or _extract_json_object(raw)

    if not isinstance(parsed, dict):
        # Fallback: return at least targets and a minimal structure.
        return {
            "profile_summary": {
                "demographics": {
                    "age": age,
                    "gender": gender,
                    "weight_kg": weight,
                    "height_cm": height,
                    "activity_level": activity_level,
                    "goal": goal,
                    "country": country,
                },
                "assumptions": ["LLM output could not be parsed as JSON; returning targets only."],
                "constraints": {
                    "dietary_restrictions": dietary_restrictions or [],
                    "allergies": allergies or [],
                    "cuisine_preferences": cuisine_preferences or [],
                    "cooking_time_per_day_minutes": cooking_time_per_day_minutes,
                    "cooking_level": cooking_level,
                    "equipment": equipment or [],
                },
                "budget": {
                    "currency": currency,
                    "budget_per_day": budget_per_day,
                    "budget_per_week": budget_per_week,
                    "estimated_cost_per_day": 0,
                    "estimated_cost_per_week": 0,
                },
            },
            "targets": targets,
            "portion_guidelines": portion_guidelines,
            "meal_plan": {"days": []},
            "grocery_list": {"items": [], "estimated_total_cost": 0},
            "prep_plan": {"batch_cook_suggestions": [], "storage_notes": [], "swap_options": []},
            "tracking_tips": [],
            "raw_model_output": raw[:4000],
        }

    # Ensure targets are present and consistent with computed targets.
    parsed.setdefault("targets", targets)
    parsed["targets"].update(targets)
    return parsed
