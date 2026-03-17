from typing import Dict, Any

class Config:
    """Application configuration"""
    DEBUG = True
    DATABASE_URL = "sqlite:///diet_ai_agent.db"
    CHROMA_DB_PATH = "chroma_db"
    OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
    MODEL_CONFIG = {
        "llm": {
            "model": "stepfun/step-3.5-flash:free",
            "temperature": 0.7,
            "max_tokens": 4000
        },
        "embeddings": {
            "model": "nvidia/llama-nemotron-embed-vl-1b-v2:free"
        }
    }

# Global config instance
config = Config()