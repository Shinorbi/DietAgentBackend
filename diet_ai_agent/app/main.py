from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.vectorstore.chroma_store import chroma_store
from app.database.db import create_connection, create_tables
import uvicorn
import sys
import os
def create_app():
    """Create and configure the FastAPI app"""
    app = FastAPI(
        title="Diet AI Agent",
        description="An AI-powered diet and nutrition assistant",
        version="1.0.0"
    )

    # Allow all CORS requests (for development/testing)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "message": "Diet AI Agent is running"}

    # Include API routes
    app.include_router(api_router, prefix="/api")

    # Initialize database
    conn = create_connection()
    if conn:
        create_tables(conn)

    # Initialize vector store (no initialization needed for simple vector store)
    print("Vector store initialized")

    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)