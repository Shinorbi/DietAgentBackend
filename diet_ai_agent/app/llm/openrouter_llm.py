from langchain_openai import ChatOpenAI
import os

def get_llm():
    """Initialize and return the StepFun LLM instance"""
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing API key. Set OPENROUTER_API_KEY (preferred) or OPENAI_API_KEY.")
    llm = ChatOpenAI(
        model="stepfun/step-3.5-flash:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=api_key,
        temperature=0.3,
        # max_tokens=15000,
        # Best-effort: force valid JSON object output (OpenAI-compatible).
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    return llm