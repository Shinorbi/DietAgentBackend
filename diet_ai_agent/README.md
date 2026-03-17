# Diet AI Agent

An AI-powered diet and nutrition assistant built with LangChain, FastAPI, and ChromaDB.

## Features

- **Meal Analysis**: Analyze meals and get detailed nutritional breakdowns
- **Diet Planning**: Generate personalized diet plans based on user goals
- **Food Knowledge**: Query nutrition information using vector database
- **AI Recommendations**: Get intelligent food suggestions and improvements
- **Calorie Tracking**: Calculate calories and macronutrients for meals
- **Progress Tracking**: Monitor diet progress over time

## Technology Stack

- **Framework**: FastAPI
- **AI**: LangChain with StepFun LLM
- **Embeddings**: Nemotron embeddings
- **Vector DB**: ChromaDB
- **Database**: SQLite
- **Language**: Python

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file:
   ```
   OPENAI_API_KEY=your_openrouter_key
   EMBEDDING_KEY=your_openrouter_key
   ```

## Quick Start

1. Start the API server:
   ```bash
   cd diet_ai_agent
   python app/main.py
   ```
2. The server will start on `http://localhost:8000`
3. Use the API endpoints to interact with the diet AI agent

## API Endpoints

### Create Diet Plan
```
POST /api/user/diet-plan
```
Request:
```json
{
  "weight": 70,
  "height": 170,
  "age": 25,
  "gender": "male",
  "activity_level": "moderate",
  "goal": "lose_weight"
}
```

### Log Meal
```
POST /api/meal/log
```
Request:
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

### Ask AI
```
POST /api/ask
```
Request:
```json
{
  "question": "What should I eat for dinner today?"
}
```

### Analyze Meal
```
POST /api/meal/analyze
```
Request:
```json
{
  "user_id": 1,
  "meal_type": "lunch",
  "foods": [
    {"name": "chicken", "qty": 1},
    {"name": "rice", "qty": 1}
  ]
}
```

## Example Usage

```python
from diet_ai_agent.agent.diet_agent import diet_agent

# Analyze a meal
meal = [{"name": "egg", "qty": 2}, {"name": "toast", "qty": 1}]
result = diet_agent.run(f"Analyze this meal: {meal}. Provide nutritional breakdown.")

# Get food recommendations
recommendation = diet_agent.run("What should I eat for a healthy breakfast?")
```

## Project Structure

```
diet_ai_agent/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── agent/
│   │   ├── diet_agent.py    # Main AI agent
│   │   └── prompts.py       # System prompts
│   ├── tools/
│   │   ├── calorie_tool.py  # Calorie calculation
│   │   ├── diet_planner_tool.py  # Diet planning
│   │   ├── meal_analyzer_tool.py  # Meal analysis
│   │   └── food_lookup_tool.py    # Food knowledge lookup
│   ├── services/
│   │   ├── diet_service.py  # Diet plan services
│   │   ├── meal_log_service.py  # Meal logging services
│   │   └── recommendation_service.py  # AI recommendation services
│   ├── llm/
│   │   └── openrouter_llm.py  # LLM integration
│   ├── embeddings/
│   │   └── openrouter_embeddings.py  # Embeddings integration
│   ├── vectorstore/
│   │   └── chroma_store.py  # Vector database
│   ├── database/
│   │   ├── db.py           # Database setup
│   │   └── models.py       # Data models
│   └── memory/
│       └── conversation_memory.py  # Conversation memory
├── data/
│   └── nutrition_knowledge.txt  # Nutrition knowledge data
├── requirements.txt
├── .env
└── README.md
```

## Future Improvements

- Food image recognition
- Weekly diet planning
- Grocery suggestions
- Macro tracking dashboard
- Weight prediction
- Office catering optimization
- Integration with fitness trackers
- Mobile app development

## License

MIT License