from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# User model
class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None
    created_at: Optional[datetime] = None

# Meal log model
class MealLog(BaseModel):
    id: Optional[int] = None
    user_id: int
    meal_type: str
    foods: str
    calories: float
    protein: float
    carbs: float
    fat: float
    created_at: Optional[datetime] = None

# Diet plan model
class DietPlan(BaseModel):
    id: Optional[int] = None
    user_id: int
    daily_calories: int
    protein_grams: float
    carbs_grams: float
    fat_grams: float
    created_at: Optional[datetime] = None

# Progress model
class Progress(BaseModel):
    id: Optional[int] = None
    user_id: int
    weight: float
    calories_consumed: int
    calories_burned: int
    date: datetime

# Food item model
class FoodItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

# Meal analysis model
class MealAnalysis(BaseModel):
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    foods: List[FoodItem]