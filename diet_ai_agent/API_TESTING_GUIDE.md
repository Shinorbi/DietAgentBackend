# Diet AI Agent API Testing Guide

This guide explains how to use the demo.html interface to test the Diet AI Agent API endpoints.

## Prerequisites

1. Python 3.8+ installed
2. Required packages installed (see requirements.txt)
3. API server running on port 8000

## Starting the API Server

```bash
cd diet_ai_agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

The server will start on http://localhost:8000

## Using demo.html for API Testing

Open `demo.html` in your web browser. The interface has 5 testing sections:

### 1. Meal Analysis
- **Endpoint**: POST /api/meal/analyze
- **Purpose**: Analyze nutritional content of a meal
- **Default Test**: 2 eggs + 1 toast
- **Result**: JSON response with nutritional breakdown

### 2. Diet Plan Generator
- **Endpoint**: POST /api/user/diet-plan
- **Purpose**: Generate personalized diet plan
- **Inputs**: Weight, height, age, gender, activity level, goal
- **Result**: JSON with diet plan and macros

### 3. Food Knowledge
- **Endpoint**: POST /api/ask
- **Purpose**: Query food-related knowledge
- **Default Test**: "Is egg good for weight loss?"
- **Result**: JSON with AI response

### 4. Food Recommendations
- **Endpoint**: POST /api/ask
- **Purpose**: Get meal recommendations
- **Inputs**: Meal type, goal
- **Result**: JSON with food recommendations

### 5. AI Agent Analysis
- **Endpoint**: POST /api/ask
- **Purpose**: Comprehensive meal analysis
- **Default Test**: "Analyze a meal of 2 eggs and 1 slice of toast..."
- **Result**: JSON with detailed analysis

## Available API Endpoints

### POST /api/user/diet-plan
Creates a personalized diet plan based on user data.

**Request Body:**
```json
{
  "weight": 70,
  "height": 170,
  "age": 25,
  "gender": "male",
  "activity_level": "moderate",
  "goal": "maintain_weight"
}
```

### POST /api/meal/log
Logs a meal for a user.

**Request Body:**
```json
{
  "user_id": 1,
  "meal_type": "breakfast",
  "foods": [
    {"name": "egg", "qty": 2},
    {"name": "toast", "qty": 1}
  ]
}
```

### POST /api/ask
Asks the diet AI for recommendations or information.

**Request Body:**
```json
{
  "question": "What are some healthy breakfast options for weight loss?"
}
```

### POST /api/meal/analyze
Analyzes a meal using the AI agent.

**Request Body:**
```json
{
  "user_id": 1,
  "meal_type": "breakfast",
  "foods": [
    {"name": "egg", "qty": 2},
    {"name": "toast", "qty": 1}
  ]
}
```

## Testing Workflow

1. Start the API server
2. Open demo.html in browser
3. Click any of the 5 buttons to test an endpoint
4. View the JSON response in the result area below each section
5. Modify inputs as needed for different test scenarios

## Common Test Scenarios

- Test with different user profiles (age, weight, activity level)
- Test various meal combinations
- Test different dietary goals (weight loss, gain, maintenance)
- Test edge cases (empty inputs, invalid data)

## Troubleshooting

- Ensure the API server is running before using demo.html
- Check browser console for network errors
- Verify the API endpoints are responding correctly
- Check the server logs for any backend errors