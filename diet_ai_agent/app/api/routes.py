from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.diet_service import create_diet_plan, get_macros_breakdown
from ..services.meal_log_service import log_meal, get_meal_history
from ..services.recommendation_service import get_diet_recommendations, analyze_meal_with_ai
from ..database.models import DietPlan

router = APIRouter()

# Request models
class UserDietPlanRequest(BaseModel):
    weight: float
    height: float
    age: int
    gender: str
    activity_level: str
    goal: str
    # Optional personalization (demographics/preferences/budget) for full plan output
    days: int = 7
    meals_per_day: int = 3
    country: Optional[str] = None
    currency: str = "USD"
    budget_per_day: Optional[float] = None
    budget_per_week: Optional[float] = None
    cuisine_preferences: List[str] = []
    dietary_restrictions: List[str] = []
    allergies: List[str] = []
    cooking_time_per_day_minutes: Optional[int] = None
    cooking_level: Optional[str] = None
    equipment: List[str] = []

class MealLogRequest(BaseModel):
    user_id: int
    meal_type: str
    foods: List[Dict[str, Any]]

class AskRequest(BaseModel):
    question: str

# Routes
@router.post("/user/diet-plan")
async def create_user_diet_plan(request: UserDietPlanRequest):
    """Create a personalized diet plan for a user"""
    user_data = request.dict()
    print(f"Received diet plan request: {user_data}")
    diet_plan = create_diet_plan(user_data)

    if isinstance(diet_plan, dict) and "error" in diet_plan:
        raise HTTPException(status_code=400, detail=diet_plan["error"])

    macros = get_macros_breakdown(diet_plan)
    return {
        "success": True,
        # Backwards compatible: keep macros + targets available
        "diet_plan": diet_plan,
        "macros": macros
    }

@router.post("/meal/log")
async def log_user_meal(request: MealLogRequest):
    """Log a meal for a user"""
    result = log_meal(request.user_id, request.meal_type, request.foods)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/ask")
async def ask_diet_ai(request: AskRequest):
    """Ask the diet AI for recommendations"""
    result = get_diet_recommendations(request.question)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/meal/analyze")
async def analyze_meal(request: MealLogRequest):
    """Analyze a meal using the AI agent"""
    result = analyze_meal_with_ai(request.foods)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result